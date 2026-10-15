"""Ingest IEEE-CIS Fraud Detection dataset to Google Cloud Storage (GCS).

Converts raw CSV files to Snappy-compressed Parquet and uploads them to the
Data Lake bucket.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import pyarrow.csv as pv
import pyarrow.parquet as pq
from google.cloud import storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Base paths and defaults
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUCKET = os.environ.get("GCS_BUCKET_NAME", "fraud-risk-131026-data-lake")
DEFAULT_PREFIX = os.environ.get("GCS_PREFIX", "raw/ieee_cis")
DEFAULT_SOURCE = PROJECT_ROOT / "data" / "raw" / "ieee-fraud-detection"
DEFAULT_PARQUET = PROJECT_ROOT / "data" / "parquet"
DEFAULT_CREDS = PROJECT_ROOT / "credentials" / "pipeline-sa-key.json"

FILES = [
    ("train_transaction.csv", "train_transaction.parquet"),
    ("train_identity.csv", "train_identity.parquet"),
]


def convert_to_parquet(csv_path: Path, pq_path: Path) -> None:
    """Convert raw CSV to Snappy Parquet."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Source file not found: {csv_path}")

    pq_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Converting {csv_path.name} -> {pq_path.name}...")
    
    table = pv.read_csv(csv_path)
    pq.write_table(table, pq_path, compression="snappy")

    raw_mb = csv_path.stat().st_size / (1024 * 1024)
    pq_mb = pq_path.stat().st_size / (1024 * 1024)
    saved_pct = (1.0 - (pq_mb / raw_mb)) * 100.0
    logger.info(f"Done: {pq_path.name} ({raw_mb:.1f} MB -> {pq_mb:.1f} MB, saved {saved_pct:.1f}%)")


def get_storage_client(creds_path: Path) -> storage.Client:
    """Authenticate and return GCS client."""
    if creds_path.exists():
        return storage.Client.from_service_account_json(str(creds_path))
    return storage.Client()


def upload_to_gcs(client: storage.Client, bucket_name: str, local_path: Path, gcs_blob: str) -> str:
    """Upload Parquet file to GCS using chunked upload."""
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob)
    blob.chunk_size = 16 * 1024 * 1024

    logger.info(f"Uploading {local_path.name} -> gs://{bucket_name}/{gcs_blob}")
    blob.upload_from_filename(str(local_path))
    uri = f"gs://{bucket_name}/{gcs_blob}"
    logger.info(f"Uploaded: {uri} ({local_path.stat().st_size / (1024 * 1024):.1f} MB)")
    return uri


def run(
    source_dir: Path = DEFAULT_SOURCE,
    parquet_dir: Path = DEFAULT_PARQUET,
    bucket_name: str = DEFAULT_BUCKET,
    prefix: str = DEFAULT_PREFIX,
    creds_path: Path = DEFAULT_CREDS,
    skip_convert: bool = False,
    skip_upload: bool = False,
) -> None:
    """Execute conversion and ingestion."""
    # 1. Convert CSV to Parquet
    for csv_name, pq_name in FILES:
        pq_path = parquet_dir / pq_name
        if skip_convert and pq_path.exists():
            logger.info(f"Skipping conversion (already exists): {pq_path.name}")
            continue
        convert_to_parquet(source_dir / csv_name, pq_path)

    if skip_upload:
        logger.info("Upload skipped (--skip-upload enabled)")
        return

    # 2. Upload to GCS
    client = get_storage_client(creds_path)
    for _, pq_name in FILES:
        pq_path = parquet_dir / pq_name
        gcs_blob = f"{prefix.strip('/')}/{pq_name}"
        upload_to_gcs(client, bucket_name, pq_path, gcs_blob)

    logger.info("Ingestion completed successfully.")


def main():
    parser = argparse.ArgumentParser(description="Ingest IEEE-CIS dataset to GCS Parquet.")
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE, help="Raw CSV directory")
    parser.add_argument("--parquet-dir", type=Path, default=DEFAULT_PARQUET, help="Output Parquet directory")
    parser.add_argument("--bucket", type=str, default=DEFAULT_BUCKET, help="Target GCS bucket")
    parser.add_argument("--prefix", type=str, default=DEFAULT_PREFIX, help="GCS target prefix")
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDS, help="Path to SA key JSON")
    parser.add_argument("--skip-convert", action="store_true", help="Skip CSV conversion")
    parser.add_argument("--skip-upload", action="store_true", help="Skip GCS upload")
    parser.add_argument("--debug", action="store_true", help="Enable verbose DEBUG logging")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled. Verbose logging is active.")

    run(
        source_dir=args.source_dir,
        parquet_dir=args.parquet_dir,
        bucket_name=args.bucket,
        prefix=args.prefix,
        creds_path=args.credentials,
        skip_convert=args.skip_convert,
        skip_upload=args.skip_upload,
    )


if __name__ == "__main__":
    main()

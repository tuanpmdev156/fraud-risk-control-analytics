# Data Ingestion to Google Cloud Storage (GCS)

This document provides technical documentation for the batch ingestion pipeline implemented in [`scripts/ingest_to_gcs.py`](../scripts/ingest_to_gcs.py).

---

## 1. Overview

The batch ingestion script transforms raw Kaggle CSV files into columnar, compressed Parquet files and loads them into Google Cloud Storage (Data Lake) for downstream BigQuery external table queries.

```
data/raw/ieee-fraud-detection/*.csv
               │
               ▼ (PyArrow Snappy Conversion)
data/parquet/*.parquet
               │
               ▼ (16 MB Chunked Upload)
gs://<GCS_BUCKET>/raw/ieee_cis/*.parquet
```

---

## 2. Parquet Conversion & Benchmarks

Using **Apache PyArrow** with **Snappy compression**, raw transaction and identity CSVs are converted to columnar Parquet before uploading to GCS.

| File Name | Format | Rows | Columns | File Size | Space Saved |
|---|:---:|:---:|:---:|:---:|:---:|
| `train_transaction.csv` | CSV | 590,540 | 394 | **683.4 MB** | - |
| `train_transaction.parquet` | Parquet (Snappy) | 590,540 | 394 | **79.7 MB** | **~88.3%** |
| `train_identity.csv` | CSV | 144,233 | 41 | **26.5 MB** | - |
| `train_identity.parquet` | Parquet (Snappy) | 144,233 | 41 | **3.9 MB** | **~85.4%** |
| **Total** | - | - | - | **709.9 MB $\rightarrow$ 83.6 MB** | **~88.2%** |

### Benefits:
- **Reduced Network Transfer**: Uploading ~84 MB instead of ~710 MB saves network bandwidth and upload time.
- **Lower Storage & Scan Costs**: BigQuery external tables query compressed columnar Parquet significantly faster with less scanned bytes compared to raw CSV.

---

## 3. Architecture & Features

1. **Chunked Resumable Upload**:
   - Files are uploaded using a 16 MB chunk buffer (`blob.chunk_size = 16 * 1024 * 1024`), ensuring reliability for large uploads.
2. **Dual Authentication Support**:
   - Checks for a dedicated Service Account key at `credentials/pipeline-sa-key.json`.
   - If not found, seamlessly falls back to GCP Application Default Credentials (`gcloud auth application-default login`).
3. **Idempotency & Flexibility**:
   - Supports skipping conversion (`--skip-convert`) if Parquet files already exist locally.
   - Supports skipping upload (`--skip-upload`) for local-only testing and validation.

---

## 4. CLI Usage & Parameters

### Execution Examples

```bash
# Standard run (Convert CSV -> Parquet and upload to GCS)
python scripts/ingest_to_gcs.py

# Override target bucket and prefix
python scripts/ingest_to_gcs.py --bucket my-lake-bucket --prefix raw/ieee_cis

# Local conversion only (skip GCS upload)
python scripts/ingest_to_gcs.py --skip-upload

# Upload existing Parquet only (skip conversion)
python scripts/ingest_to_gcs.py --skip-convert

# Specify custom service account key
python scripts/ingest_to_gcs.py --credentials path/to/sa-key.json
```

### CLI Parameter Reference

| Argument | Type | Default | Description |
|---|---|---|---|
| `--source-dir` | `Path` | `data/raw/ieee-fraud-detection` | Directory containing raw CSV files |
| `--parquet-dir` | `Path` | `data/parquet` | Target directory for generated Parquet files |
| `--bucket` | `str` | `fraud-risk-131026-data-lake` (or `$GCS_BUCKET_NAME`) | Destination GCS bucket name |
| `--prefix` | `str` | `raw/ieee_cis` (or `$GCS_PREFIX`) | Blob prefix inside the bucket |
| `--credentials` | `Path` | `credentials/pipeline-sa-key.json` | Path to GCP Service Account JSON key |
| `--skip-convert` | `flag` | `False` | Skip CSV conversion if target Parquet exists |
| `--skip-upload` | `flag` | `False` | Skip upload to GCS |

---

## 5. Verification

Verify uploaded blobs in Google Cloud Storage:

```bash
gcloud storage ls gs://YOUR_BUCKET_NAME/raw/ieee_cis/
```

Expected output:
```
gs://YOUR_BUCKET_NAME/raw/ieee_cis/train_identity.parquet
gs://YOUR_BUCKET_NAME/raw/ieee_cis/train_transaction.parquet
```


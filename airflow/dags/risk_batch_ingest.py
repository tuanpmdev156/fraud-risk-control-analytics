"""Airflow DAG: risk_batch_ingest

Automates the batch ingestion pipeline for the IEEE-CIS Fraud Detection dataset:
1. Verify raw CSV source files exist.
2. Convert raw CSV to Snappy-compressed Parquet.
3. Upload Parquet files to Google Cloud Storage (Data Lake).
4. Create BigQuery External Tables in the 'raw' dataset.
5. Perform Data Quality checks (row counts & null checks).
"""

from __future__ import annotations

import os
import requests
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCheckOperator,
    BigQueryInsertJobOperator,
)
from airflow.providers.google.cloud.transfers.local_to_gcs import (
    LocalFilesystemToGCSOperator,
)

# ---------------------------------------------------------------------------
# Pipeline Configuration & Constants
# ---------------------------------------------------------------------------
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "fraud-risk-analytics-131026")
GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "fraud-risk-131026-data-lake")
BQ_DATASET = os.environ.get("BQ_DATASET_RAW", "raw")
GCS_PREFIX = "raw/ieee_cis"

# Paths inside Airflow container (mapped via docker-compose volumes)
AIRFLOW_HOME = Path(os.environ.get("AIRFLOW_HOME", "/opt/airflow"))
DATA_DIR = AIRFLOW_HOME / "data"
RAW_DIR = DATA_DIR / "raw" / "ieee-fraud-detection"
PARQUET_DIR = DATA_DIR / "parquet"

TRANSACTION_FILE = "train_transaction"
IDENTITY_FILE = "train_identity"

EXPECTED_TRANSACTIONS = 590540
EXPECTED_IDENTITIES = 144233

# Simulate error task
# 'None' to run normal
SIMULATE_FAIL_TASK = "None" 
#SIMULATE_FAIL_TASK = "upload_transaction_to_gcs"

# ---------------------------------------------------------------------------
# Python Task Callables
# ---------------------------------------------------------------------------
def check_raw_files(**context) -> None:
    """Verify that raw CSV files exist and are not empty before proceeding."""
    if SIMULATE_FAIL_TASK == "check_raw_data":
        raise RuntimeError("SIMULATED ERROR at check_raw_data")
    files = [
        RAW_DIR / f"{TRANSACTION_FILE}.csv",
        RAW_DIR / f"{IDENTITY_FILE}.csv",
    ]
    for file_path in files:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Required source file missing: {file_path}. "
                "Ensure dataset is placed in data/raw/ieee-fraud-detection/"
            )
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb == 0:
            raise ValueError(f"Source file is empty: {file_path}")
        print(f"Verified source file: {file_path.name} ({file_size_mb:.2f} MB)")

def convert_csv_to_parquet(file_base_name: str, **context) -> str:
    """Convert a CSV file to Snappy-compressed Parquet using PyArrow."""
    import pyarrow.csv as pv
    import pyarrow.parquet as pq
    
    csv_path = RAW_DIR / f"{file_base_name}.csv"
    pq_path = PARQUET_DIR / f"{file_base_name}.parquet"
    current_task_id = context.get("task_instance").task_id
    
    if SIMULATE_FAIL_TASK == current_task_id:
        raise RuntimeError(f"SIMULATED ERROR at {current_task_id}")

    if not csv_path.exists():
        raise FileNotFoundError(f"Source CSV not found: {csv_path}")

    PARQUET_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Reading CSV: {csv_path}...")
    table = pv.read_csv(csv_path)

    if "TransactionID" not in table.column_names:
        raise ValueError("Schema Drift: Missing required column 'TransactionID'")

    print(f"Convert to Parquet: {pq_path} ({table.num_rows} rows, {table.num_columns} cols)...")
    pq.write_table(table, pq_path, compression="snappy")

    csv_mb = csv_path.stat().st_size / (1024 * 1024)
    pq_mb = pq_path.stat().st_size / (1024 * 1024)
    saved = (1.0 - (pq_mb / csv_mb)) * 100.0
    print(f"Conversion complete: {pq_path.name} ({csv_mb:.1f}MB -> {pq_mb:.1f}MB, saved {saved:.1f}%)")
    return str(pq_path)

def slack_alert_on_failure(context) -> None:
    """
    Trigger when reaching retry limit with FAILED status
    """
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("SLACK_WEBHOOK_URL is not configured properly.")
        return

    ti = context.get("task_instance")
    dag_id = ti.dag_id
    task_id = ti.task_id
    logical_date = context.get("logical_date").strftime("%Y-%m-%d %H:%M:%S UTC")
    
    encoded_run_id = urllib.parse.quote(ti.run_id, safe="")
    log_url = f"http://localhost:8080/dags/{dag_id}/grid?tab=logs&dag_run_id={encoded_run_id}&task_id={task_id}"
    exception = context.get("exception", "No exception message provided")

    # Exception's message 
    error_summary = str(exception)[:350]

    slack_msg = {
        "text": f":rotating_light: Pipeline Alert: Task {task_id} FAILED trong DAG {dag_id}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 Airflow Ingestion Task Failure",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*DAG:*\n`{dag_id}`"},
                    {"type": "mrkdwn", "text": f"*Task:*\n`{task_id}`"},
                    {"type": "mrkdwn", "text": f"*Execution Date:*\n{logical_date}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n*P1 - High (Retries Exhausted)*"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Root Cause / Error Message:*\n```{error_summary}```"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "🔍 Inspect Task Log"},
                        "url": log_url,
                        "style": "danger"
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=slack_msg, timeout=10)
        response.raise_for_status()
        print(f"[INFO] Slack alert is sent for task={task_id}")
    except Exception as exc:
        print(f"[ERROR] Cannot send arlet to Slack: {exc}")


# ---------------------------------------------------------------------------
# DAG Definition
# ---------------------------------------------------------------------------
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
    "on_failure_callback": slack_alert_on_failure
}

with DAG(
    dag_id="risk_batch_ingest",
    default_args=default_args,
    description="Batch Ingestion: IEEE-CIS Fraud Dataset -> GCS Parquet -> BigQuery External Tables",
    schedule_interval=None,  # Triggered manually or as batch ad-hoc
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1
) as dag:

    # 1. Check raw CSV files
    task_check_raw_data = PythonOperator(
        task_id="check_raw_data",
        python_callable=check_raw_files,
    )

    # 2. Convert CSV to Parquet (parallel tasks)
    task_convert_transaction = PythonOperator(
        task_id="convert_transaction_to_parquet",
        python_callable=convert_csv_to_parquet,
        op_kwargs={"file_base_name": TRANSACTION_FILE},
    )

    task_convert_identity = PythonOperator(
        task_id="convert_identity_to_parquet",
        python_callable=convert_csv_to_parquet,
        op_kwargs={"file_base_name": IDENTITY_FILE},
    )

    # 3. Upload Parquet files to GCS
    task_upload_transaction_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_transaction_to_gcs",
        src=(
            "/non_existent_file.parquet"
            if SIMULATE_FAIL_TASK == "upload_transaction_to_gcs"
            else str(PARQUET_DIR / f"{TRANSACTION_FILE}.parquet")
        ),
        dst=f"{GCS_PREFIX}/{TRANSACTION_FILE}.parquet",
        bucket=GCS_BUCKET,
    )

    task_upload_identity_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_identity_to_gcs",
        src=str(PARQUET_DIR / f"{IDENTITY_FILE}.parquet"),
        dst=f"{GCS_PREFIX}/{IDENTITY_FILE}.parquet",
        bucket=GCS_BUCKET,
    )

    # 4. Create BigQuery External Tables
    sql_create_ext_transaction = f"""
    CREATE OR REPLACE EXTERNAL TABLE `{GCP_PROJECT_ID}.{BQ_DATASET}.ext_transaction`
    OPTIONS (
      format = 'PARQUET',
      uris = ['gs://{GCS_BUCKET}/{GCS_PREFIX}/{TRANSACTION_FILE}.parquet']
    );
    """

    sql_create_ext_identity = f"""
    CREATE OR REPLACE EXTERNAL TABLE `{GCP_PROJECT_ID}.{BQ_DATASET}.ext_identity`
    OPTIONS (
      format = 'PARQUET',
      uris = ['gs://{GCS_BUCKET}/{GCS_PREFIX}/{IDENTITY_FILE}.parquet']
    );
    """

    task_create_bq_ext_transaction = BigQueryInsertJobOperator(
        task_id="create_bq_ext_transaction",
        configuration={
            "query": {
                "query": sql_create_ext_transaction,
                "useLegacySql": False,
            }
        },
    )

    task_create_bq_ext_identity = BigQueryInsertJobOperator(
        task_id="create_bq_ext_identity",
        configuration={
            "query": {
                "query": sql_create_ext_identity,
                "useLegacySql": False,
            }
        },
    )

    # 5. Data Quality Audits
    task_audit_transaction = BigQueryCheckOperator(
        task_id="audit_transaction_data_quality",
        sql=f"""
        SELECT
          COUNT(1) = {EXPECTED_TRANSACTIONS}
          AND COUNTIF(TransactionID IS NULL) = 0
        FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.ext_transaction`
        """,
        use_legacy_sql=False,
    )

    task_audit_identity = BigQueryCheckOperator(
        task_id="audit_identity_data_quality",
        sql=f"""
        SELECT
          COUNT(1) = {EXPECTED_IDENTITIES}
          AND COUNTIF(TransactionID IS NULL) = 0
        FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.ext_identity`
        """,
        use_legacy_sql=False,
    )

    # -----------------------------------------------------------------------
    # Task Dependencies Graph
    # -----------------------------------------------------------------------
    task_check_raw_data >> [task_convert_transaction, task_convert_identity]

    task_convert_transaction >> task_upload_transaction_gcs >> task_create_bq_ext_transaction >> task_audit_transaction
    task_convert_identity >> task_upload_identity_gcs >> task_create_bq_ext_identity >> task_audit_identity


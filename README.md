# Financial Fraud Detection & Risk Analytics

![GCP](https://img.shields.io/badge/Cloud-Google_Cloud-4285F4?logo=googlecloud&logoColor=white)
![Terraform](https://img.shields.io/badge/IaC-Terraform-844FBA?logo=terraform&logoColor=white)
![Airflow](https://img.shields.io/badge/Orchestration-Airflow_2.11-017CEE?logo=apacheairflow&logoColor=white)
![dbt](https://img.shields.io/badge/Transform-dbt-FF694B?logo=dbt&logoColor=white)
![Evidence](https://img.shields.io/badge/Dashboard-Evidence.dev-4F46E5?logo=data:image/svg+xml;base64,&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Dataset & Exploratory Data Analysis (EDA)](#2-dataset--exploratory-data-analysis-eda)
- [3. System Architecture](#3-system-architecture)
- [4. Tech Stack](#4-tech-stack)
- [5. Quick Start & Reproduction Guide](#5-quick-start--reproduction-guide)
  - [Prerequisites](#prerequisites)
  - [5.1. Clone & Install Dependencies](#51-clone--install-dependencies)
  - [5.2. GCP Authentication](#52-gcp-authentication)
  - [5.3. Provision Infrastructure (Terraform)](#53-provision-infrastructure-terraform)
  - [5.4. Verify Infrastructure](#54-verify-infrastructure)
  - [5.5. Download Dataset (IEEE-CIS Fraud Detection)](#55-download-dataset-ieee-cis-fraud-detection)
  - [5.6. Data Exploration & Validation](#56-data-exploration--validation)
  - [5.7. Standalone Ingestion to GCS Data Lake](#57-standalone-ingestion-to-gcs-data-lake)
  - [5.8. Orchestrate End-to-End Pipeline with Apache Airflow](#58-orchestrate-end-to-end-pipeline-with-apache-airflow)
  - [5.9. Data Warehouse Transformations & Data Quality (dbt)](#59-data-warehouse-transformations--data-quality-dbt)
  - [5.10. BI-as-Code Dashboard (Evidence.dev) & CI/CD Deployment](#510-bi-as-code-dashboard-evidencedev--cicd-deployment)

---

## 1. Project Overview

Card fraud costs the global economy over **$32 billion per year**. Because traditional rule-based systems miss sophisticated fraud patterns, payment processors need scalable, data-driven analytical infrastructure to detect anomalies and monitor risk exposure.

This project builds a production-grade **end-to-end Data Engineering pipeline** that ingests, models, and visualises **590,540 real-world e-commerce transactions** from Vesta Corporation ([IEEE-CIS dataset](https://www.kaggle.com/competitions/ieee-fraud-detection)) to answer:
- **What is the fraud rate across product categories, card networks, and device types?**
- **How does fraud volume and monetary exposure ($M) evolve over time?**
- **Which transaction segments and amount tiers (`micro` to `critical`) carry the highest risk?**

**Key Engineering Highlights**:
- **Automated Orchestration**: *Apache Airflow* DAG handling CSV validation, Snappy Parquet compression, GCS & BigQuery External Table provisioning, *dbt* runs, and *Slack* failure alerts.
- **Optimized Medallion Warehouse**: BigQuery `raw` ➔ `staging` ➔ `production` layers with partitioning, clustering, deduplication, and anomalous record quarantine routing.
- **Data Quality & Governance**: Fail-fast schema drift checks via *PyArrow* and 15 automated *dbt* schema & singular tests.
- **BI-as-Code & CI/CD**: Interactive *Evidence.dev* dashboard auto-deployed to GitHub Pages via *GitHub Actions* (`push` & Airflow `workflow_dispatch`).

---

## 2. Dataset & Exploratory Data Analysis (EDA)

| Attribute | Detail |
|---|---|
| **Source** | Vesta Corporation (real production data, anonymised) |
| **Size** | 590,540 transactions + 144,233 identity records (~710 MB raw CSVs) |
| **Fraud rate** | 3.50% (20,663 flagged transactions — severe class imbalance) |
| **Features** | 400+ (transaction amount, card type, email domains, device info, match flags) |
| **Time span** | ~6 months of e-commerce activity |
| **Kaggle page** | [ieee-fraud-detection](https://www.kaggle.com/competitions/ieee-fraud-detection) |

**Key EDA & Architectural Decisions**:
- **Conversion Efficiency**: Compressed raw CSVs (710 MB) into Snappy Parquet (83.6 MB, **~88% storage saving**).
- **Distribution Insights**: Identified severe class imbalance (`3.50%` fraud) and heavy transaction amount right-skewness requiring log-scale profiling and risk-tier bucketing (`micro` to `critical`).
- **Warehouse Optimization**: Pruned 400+ sparse raw columns down to **18–23 core attributes** (**~95.8% memory reduction**), partitioned by `transaction_date`, and clustered by `product_code`, `card_network`, `is_fraud`.

> Detailed EDA & Architectural Decision: [`docs/data_exploration.md`](docs/data_exploration.md)  
> Standardized Profiling Notebook: [`notebooks/data_exploration.ipynb`](notebooks/data_exploration.ipynb)

---

## 3. System Architecture

![System Architecture](docs/images/system_architecture.png)  
*Figure: System Architecture.*

---

## 4. Tech Stack

| Component | Technology | Detail |
|---|---|---|
| **Cloud** | Google Cloud Platform | BigQuery serverless DW + native GCS Data Lake integration |
| **IaC** | Terraform | Declarative infra: GCS, BigQuery datasets (`raw`, `staging`, `production`), IAM |
| **Python Env** | `uv` (Astral) | 10–100x faster than pip, deterministic lockfile (`uv.lock`) |
| **Batch Orchestration** | Apache Airflow 2.11 (Docker) | Automated DAG management with auto-retry, DQ gates & Slack webhook alerting |
| **Transformation** | dbt-core + dbt-bigquery | Modular SQL ELT with custom macros, schema/singular testing & lineage |
| **DW Design** | Medallion (`raw`→`staging`→`production`) | Partitioned by `transaction_date`, clustered by `product_code`, `card_network`, `is_fraud` |
| **BI Dashboard** | Evidence.dev (BI-as-Code) | Version-controlled Markdown + SQL analytics with static site generation |
| **CI/CD** | GitHub Actions | Automated BigQuery source extraction, static build & GitHub Pages deployment |

---

## 5. Quick Start & Reproduction Guide

### Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
- [Terraform](https://developer.hashicorp.com/terraform/install) (>= 1.0)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
- [Node.js](https://nodejs.org/) (>= 18.0, for Evidence.dev dashboard)

### 5.1. Clone & Install Dependencies

```bash
git clone https://github.com/tuanpmdev156/fraud-risk-control-analytics.git
cd fraud-risk-control-analytics
uv sync
```

### 5.2. GCP Authentication

```bash
gcloud auth login
gcloud auth application-default login
```

### 5.3. Provision Infrastructure (Terraform)

```bash
cd terraform
# Edit terraform.tfvars with your GCP project ID and bucket name

terraform init
terraform plan
terraform apply
cd ..
```

> **Note**: `terraform apply` provisions the GCS Data Lake bucket, BigQuery datasets (`raw`, `staging`, `production`), IAM roles, and automatically exports the Service Account JSON key to `credentials/pipeline-sa-key.json` for local Airflow, Python, and dbt authentication.

### 5.4. Verify Infrastructure

```bash
terraform -chdir=terraform output
gcloud storage ls
bq ls --project_id=YOUR_PROJECT_ID
```

### 5.5. Download Dataset (IEEE-CIS Fraud Detection)

Download `train_transaction.csv` and `train_identity.csv` from the [IEEE-CIS Fraud Detection Kaggle competition](https://www.kaggle.com/c/ieee-fraud-detection/data) and place them in `data/raw/ieee-fraud-detection/`:

```bash
mkdir -p data/raw/ieee-fraud-detection

# Option 1: Using Kaggle CLI (requires ~/.kaggle/kaggle.json)
uv run kaggle competitions download -c ieee-fraud-detection -f train_transaction.csv -p data/raw/ieee-fraud-detection
uv run kaggle competitions download -c ieee-fraud-detection -f train_identity.csv -p data/raw/ieee-fraud-detection
unzip "data/raw/ieee-fraud-detection/*.zip" -d data/raw/ieee-fraud-detection/

# Option 2: Manually download from Kaggle UI and extract into:
# data/raw/ieee-fraud-detection/train_transaction.csv
# data/raw/ieee-fraud-detection/train_identity.csv
```

### 5.6. Data Exploration & Validation

Inspect distributions, label imbalance, and schema integrity:
- **Notebook**: [`notebooks/data_exploration.ipynb`](notebooks/data_exploration.ipynb) (numerical profiling & memory benchmarks)
- **Exploratory Data Analysis**: [`docs/data_exploration.md`](docs/data_exploration.md)
```bash
uv run jupyter lab notebooks/data_exploration.ipynb
```

### 5.7. Standalone Ingestion to GCS Data Lake

Run [`scripts/ingest_to_gcs.py`](scripts/ingest_to_gcs.py) to convert raw CSVs to Snappy Parquet (**~88% compression**) and upload to GCS:

```bash
# Standard execution (Convert CSV -> Parquet and upload to GCS)
python scripts/ingest_to_gcs.py

# Optional: upload only / convert only
python scripts/ingest_to_gcs.py --skip-convert  # upload only
python scripts/ingest_to_gcs.py --skip-upload   # convert only
```

Verify uploaded objects in GCS:
```bash
gcloud storage ls gs://YOUR_BUCKET_NAME/raw/ieee_cis/
```

📖 **Full Ingestion Guide, Benchmarks & CLI Options**: [`docs/ingestion_to_gcs.md`](docs/ingestion_to_gcs.md)

---

### 5.8. Orchestrate End-to-End Pipeline with Apache Airflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   AIRFLOW DAG: risk_batch_ingest (12 Tasks)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                            [ check_raw_data ]                               │
│                                     │                                       │
│                   ┌─────────────────┴─────────────────┐                     │
│                   ▼                                   ▼                     │
│   [ convert_transaction_to_parquet ]   [ convert_identity_to_parquet ]      │
│                   │                                   │                     │
│                   ▼                                   ▼                     │
│     [ upload_transaction_to_gcs ]         [ upload_identity_to_gcs ]        │
│                   │                                   │                     │
│                   ▼                                   ▼                     │
│     [ create_bq_ext_transaction ]         [ create_bq_ext_identity ]        │
│                   │                                   │                     │
│                   ▼                                   ▼                     │
│  [ audit_transaction_data_quality ]     [ audit_identity_data_quality ]     │
│                   │                                   │                     │
│                   └─────────────────┬─────────────────┘                     │
│                                     ▼                                       │
│                               [ dbt_run ]                                   │
│                    (Staging Views & Production Marts)                       │
│                                     │                                       │
│                                     ▼                                       │
│                              [ dbt_test ]                                   │
│                     (15 Schema & Singular DQ Tests)                         │
│                                     │                                       │
│                                     ▼                                       │
│                        [ trigger_evidence_deploy ]                          │
│                  (GitHub Actions workflow_dispatch ──► Pages)               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│   Resilience: Auto-Retry (2x, 3m delay) ──► Slack Incident Alert (Webhook)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Pipeline Overview (12 Tasks)
1. **`check_raw_data`**: Verifies that local raw CSV files (`train_transaction.csv`, `train_identity.csv`) exist and are not empty before downstream execution.

2. **`convert_transaction_to_parquet`**: Converts `train_transaction.csv` to Snappy-compressed Parquet (**~88.3% storage saving**) with PyArrow schema validation.

3. **`convert_identity_to_parquet`**: Converts `train_identity.csv` to Snappy-compressed Parquet (**~85.4% storage saving**) in parallel with transaction conversion.

4. **`upload_transaction_to_gcs`**: Uploads `train_transaction.parquet` into the GCS Data Lake (`gs://<bucket>/raw/ieee_cis/`).

5. **`upload_identity_to_gcs`**: Uploads `train_identity.parquet` into the GCS Data Lake (`gs://<bucket>/raw/ieee_cis/`).

6. **`create_bq_ext_transaction`**: Provisions the `raw.ext_transaction` External Table in BigQuery pointing directly to GCS Parquet.

7. **`create_bq_ext_identity`**: Provisions the `raw.ext_identity` External Table in BigQuery pointing directly to GCS Parquet.

8. **`audit_transaction_data_quality`**: Data Quality gate validating exact transaction row count (**590,540** rows) and primary key integrity (`TransactionID IS NOT NULL`).

9. **`audit_identity_data_quality`**: Data Quality gate validating exact identity row count (**144,233** rows) and primary key integrity (`TransactionID IS NOT NULL`).

10. **`dbt_run`**: Executes all dbt Staging views (`stg_transaction`, `stg_identity`, `stg_quarantined_transaction`) and Production Mart tables (`fct_transaction`, `fraud_risk_summary`).

11. **`dbt_test`**: Runs 15 automated schema (`unique`, `not_null`, `accepted_values`) and singular business assertion tests across staging and mart layers.

12. **`trigger_evidence_deploy`**: Dispatches a `workflow_dispatch` event via the GitHub REST API to trigger `.github/workflows/deploy-evidence.yml`, rebuilding and deploying the Evidence.dev dashboard to GitHub Pages only after all upstream checks and dbt tests succeed.

![Airflow Batch Pipeline Success](docs/images/airflow_dag_success.png)  
*Figure: Airflow batch ingestion pipeline executing all tasks successfully.*

#### Data Quality & External Table Verification
BigQuery external tables are validated immediately upon ingestion to guarantee data integrity:

![BigQuery Raw Layer Verification](docs/images/bq_raw_verification.png)  
*Figure: BigQuery SQL audit verifying exact row counts (590,540 transactions, 144,233 identities).*

#### Pipeline Reliability, Schema Drift Protection & Slack Alerts

The batch pipeline is engineered for production resilience:

- **Auto-Retry**: Tasks automatically retry 2 times (spaced 3 minutes apart) to recover from transient network or API errors.
- **Safe Reruns (Idempotent)**: Overwriting objects in GCS and executing `CREATE OR REPLACE EXTERNAL TABLE` in BigQuery guarantees that re-running the DAG never produces duplicate records.
- **Schema Drift Fail-Fast**: PyArrow enforces required column checks (`TransactionID`, `isFraud`, `TransactionAmt`) during conversion prior to GCS upload.
- **Real-time Slack Incident Alerting**: Configured via `on_failure_callback` to dispatch rich Slack alerts containing DAG ID, Task ID, Execution Date, and direct log links upon retry exhaustion.

![Airflow Task Retry Simulation](docs/images/airflow_task_retry.png)  
*Figure: Simulated task failure demonstrating auto-retry mechanism before marking as failed.*

![Slack Incident Alert](docs/images/slack_failure_alert.png)  
*Figure: Real-time Slack incident notification with direct link to task logs.*

![Airflow Auto-Retry & Slack Alert Demo](docs/images/airflow-slack-alert-optimized.gif)  
*Figure: End-to-end demonstration of Airflow task auto-retry and real-time Slack incident alerting.*

#### Quick Commands
```bash
# 1. Configure Airflow environment variables
cp airflow/.env.example airflow/.env
# Edit airflow/.env to set GCP_PROJECT_ID, GCS_BUCKET_NAME,
# and optional SLACK_WEBHOOK_URL, GITHUB_TOKEN, GITHUB_REPO, GITHUB_WORKFLOW_FILE

# 2. Start Airflow cluster (Postgres, Webserver, Scheduler)
docker compose -f airflow/docker-compose.yaml up -d --build

# 3. View Airflow Web UI
# URL: http://localhost:8080 (Username: admin | Password: admin)

# 4. Unpause and trigger the DAG via CLI or Web UI
docker compose -f airflow/docker-compose.yaml exec airflow-scheduler airflow dags unpause risk_batch_ingest
docker compose -f airflow/docker-compose.yaml exec airflow-scheduler airflow dags trigger risk_batch_ingest
```
---

### 5.9. Data Warehouse Transformations & Data Quality (dbt)

The [`dbt_fraud_risk_control/`](dbt_fraud_risk_control) project implements a Medallion ELT architecture on BigQuery with built-in deduplication, quarantine routing, and automated testing.

#### Medallion Architecture Models
- **Staging Layer (`staging` — Views)**:
  - [`stg_transaction.sql`](dbt_fraud_risk_control/models/staging/stg_transaction.sql): Prunes 400+ columns to 18 core fields, derives timestamps, buckets amounts via the [`classify_amount`](dbt_fraud_risk_control/macros/classify_amount.sql) macro, and deduplicates by `transaction_id` (`ROW_NUMBER()`).
  - [`stg_identity.sql`](dbt_fraud_risk_control/models/staging/stg_identity.sql): Standardizes identity fields, normalizes OS/browser strings, and deduplicates records.
  - [`stg_quarantined_transaction.sql`](dbt_fraud_risk_control/models/staging/stg_quarantined_transaction.sql): Routes anomalous records (`transaction_amount <= 0` or invalid `is_fraud`) with diagnostic `quarantine_reason` flags.
- **Production Marts (`production` — Partitioned & Clustered Tables)**:
  - [`fct_transaction.sql`](dbt_fraud_risk_control/models/marts/fct_transaction.sql): Enriched transaction fact table joining transaction and identity data. Partitioned by `transaction_date`, clustered by `product_code`, `card_network`, `is_fraud`.
  - [`fraud_risk_summary.sql`](dbt_fraud_risk_control/models/marts/fraud_risk_summary.sql): Daily aggregated risk metrics. Partitioned by `transaction_date`, clustered by `card_network`, `product_code`, `device_type`.

#### Automated Data Quality Tests
- **Generic Schema Tests**: `unique`, `not_null`, and `accepted_values` enforced across staging and mart models ([`staging/schema.yml`](dbt_fraud_risk_control/models/staging/schema.yml), [`marts/schema.yml`](dbt_fraud_risk_control/models/marts/schema.yml)).
- **Singular Business Assertions**:
  - [`assert_positive_amounts.sql`](dbt_fraud_risk_control/tests/assert_positive_amounts.sql): Asserts zero records have `transaction_amount <= 0` in `fct_transaction`.
  - [`assert_valid_fraud_rate.sql`](dbt_fraud_risk_control/tests/assert_valid_fraud_rate.sql): Asserts aggregated `fraud_rate` values in `fraud_risk_summary` strictly remain within `[0, 100]%`.

#### Profile Setup & Quick Commands

Create `dbt_fraud_risk_control/profiles.yml` (git-ignored for security):
```yaml
dbt_fraud_risk_control:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: "{{ env_var('GCP_PROJECT_ID', 'YOUR_PROJECT_ID') }}"
      dataset: dev
      threads: 4
      keyfile: "{{ env_var('DBT_GOOGLE_KEYFILE', '../credentials/pipeline-sa-key.json') }}"
      location: "{{ env_var('DBT_LOCATION', 'us-central1') }}"
      priority: interactive
      job_execution_timeout_seconds: 300
      job_retries: 1
```

Run transformations and tests locally:
```bash
cd dbt_fraud_risk_control

# Verify BigQuery connection
uv run dbt debug --profiles-dir .

# Run all staging and production models
uv run dbt run --profiles-dir .

# Execute schema and singular data quality tests
uv run dbt test --profiles-dir .

# Generate and serve interactive dbt lineage documentation
uv run dbt docs generate --profiles-dir .
uv run dbt docs serve --profiles-dir .
```

---

### 5.10. BI-as-Code Dashboard (Evidence.dev) & CI/CD Deployment


![Evidence.dev Risk Analytics Dashboard](docs/images/evidence_dashboard.png)  
*🌐 **Live Dashboard**: [https://tuanpmdev156.github.io/fraud-risk-control-analytics/](https://tuanpmdev156.github.io/fraud-risk-control-analytics/)*

Interactive risk dashboard built with **Evidence.dev** ([`evidence/pages/index.md`](evidence/pages/index.md)), querying BigQuery production marts via version-controlled SQL in [`evidence/sources/bigquery/`](evidence/sources/bigquery).



#### Key Analytics Views
- **Executive KPIs**: Tracks total transactions (**590,540**), overall fraud rate (**3.50%**), fraud exposure ($M), and highest-risk product (`C`).
- **Temporal Trend**: Daily transaction volume vs. confirmed fraud occurrences over time.
- **Multi-Dimensional Breakdowns**: Fraud distribution across *Product Code*, *Card Network*, *Device Type*, and *Transaction Amount Buckets* (`micro` to `critical`), backed by searchable audit tables.

#### Local Development & Build
```bash
cd evidence
npm install        # Install dependencies
npm run sources    # Extract BigQuery marts into local DuckDB/Parquet cache
npm run dev        # Start local server at http://localhost:3000
npm run build      # Build static site to evidence/build/
```

#### Automated CI/CD ([`.github/workflows/deploy-evidence.yml`](.github/workflows/deploy-evidence.yml))
- **Triggers**: Automatically dispatched by Airflow (`trigger_evidence_deploy` via `workflow_dispatch`) after `dbt test` passes, or on code pushes to `main` (`evidence/**`).
- **Execution**: Authenticates to BigQuery via GitHub Secrets, runs `npm run sources && npm run build`, and deploys the static dashboard to **GitHub Pages**.


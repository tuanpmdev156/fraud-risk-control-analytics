# Financial Fraud Detection & Risk Analytics

![GCP](https://img.shields.io/badge/Cloud-Google_Cloud-4285F4?logo=googlecloud&logoColor=white)
![Terraform](https://img.shields.io/badge/IaC-Terraform-844FBA?logo=terraform&logoColor=white)
![Airflow](https://img.shields.io/badge/Orchestration-Airflow_2.11-017CEE?logo=apacheairflow&logoColor=white)
![Redpanda](https://img.shields.io/badge/Streaming-Redpanda-E4405F?logo=apachekafka&logoColor=white)
![dbt](https://img.shields.io/badge/Transform-dbt-FF694B?logo=dbt&logoColor=white)
![Looker Studio](https://img.shields.io/badge/Dashboard-Looker_Studio-4285F4?logo=looker&logoColor=white)
![AI](https://img.shields.io/badge/AI-LLM_Narration-8A2BE2?logo=openai&logoColor=white)

---

## 1. Problem Statement

Credit card and electronic payment fraud cause tens of billions of dollars in losses globally each year. Traditional rule-based systems are no longer flexible enough to cope with sophisticated fraud behaviors.

This project builds an **end-to-end Data Engineering system** for financial fraud detection and risk analytics, featuring:

- **Batch Processing** — Large-scale historical transaction analysis to identify risk patterns
- **Real-time Streaming** — Low-latency event simulation and ingestion via Redpanda (Kafka-compatible)
- **Optimized Data Warehouse** — Medallion architecture (Raw → Staging → Production) on BigQuery with partitioning & clustering
- **Interactive BI Dashboard** — Google Looker Studio with dynamic filters and cross-filtering
- **Agentic AI Narration** — LLM-powered risk summary generation with strict anti-hallucination guardrails, stored directly in BigQuery

## 2. Dataset & Exploratory Data Analysis (EDA)

The project utilizes the benchmark **IEEE-CIS Fraud Detection** dataset ([Kaggle](https://www.kaggle.com/c/ieee-fraud-detection)):
- **Data Volume**: 590,540 transactions (~3.50% fraud rate) and 144,233 identity records.
- **Conversion Efficiency**: Compressed raw CSVs (710 MB) into Snappy Parquet (83.6 MB, **~88% space saving**).
- **Key EDA Findings**: Severe class imbalance, heavy amount right-skewness, and ~3.8x higher fraud rate in digital transactions with identity (particularly mobile devices at 10.17%).
- **DW Architecture**: Pruned 400+ raw columns down to **~20–22 core attributes** (~95.8% memory reduction), partitioned by `transaction_date` and clustered by `product_cd`, `card4`, `is_fraud`.

📖 **Detailed EDA & Architectural Decisions**: [`docs/data_exploration.md`](docs/data_exploration.md)  
🔬 **Standardized Profiling Notebook**: [`notebooks/data_exploration.ipynb`](notebooks/data_exploration.ipynb)

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        BATCH DATA PIPELINE                              │
│                                                                         │
│  Kaggle API ──► CSV ──► Parquet (Snappy) ──► GCS Bucket (Data Lake)    │
│                                                       │                 │
│                                                       ▼                 │
│                                              BigQuery Raw (External)    │
│                                                       │                 │
│                                                       ▼                 │
│                                              dbt Staging (stg_*)        │
│                                                       │                 │
│                                                       ▼                 │
│                                              dbt Production (fct_*,     │
│                                               mart_fraud_summary)        │
│                                                       │                 │
│                                                       ▼                 │
│                                              LLM Narration Layer        │
│                                              (DeepSeek/Groq/OpenAI)     │
│                                                       │                 │
│                                                       ▼                 │
│                                              mart_ai_insights           │
│                                                       │                 │
│                                                       ▼                 │
│                                              Google Looker Studio       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                      STREAMING DATA PIPELINE                            │
│                                                                         │
│  Transaction Replayer ──► Redpanda Topic ──► Consumer ──► GCS + BQ     │
│  (producer.py)            (Kafka API)        (consumer.py)              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Rationale |
|---|---|---|
| **Cloud** | Google Cloud Platform | BigQuery serverless DW + native GCS integration |
| **IaC** | Terraform | Declarative infra: GCS, BigQuery, IAM in one `terraform apply` |
| **Python Env** | `uv` (Astral) | 10-100x faster than pip, consistent lockfile |
| **Batch Orchestration** | Apache Airflow 2.11 (Docker) | Industry-standard DAG management with retry & Web UI |
| **Streaming** | Redpanda | 100% Kafka API compatible, no JVM/Zookeeper, <1GB RAM |
| **Transformation** | dbt-core + dbt-bigquery | SQL-based ELT with lineage, testing, schema control |
| **DW Design** | Medallion (Raw→Staging→Prod) | Partitioning by `transaction_date`, clustering by `product_cd`, `card_type`, `is_fraud` |
| **AI Layer** | OpenAI SDK (Provider-Agnostic) | Flexible: DeepSeek, Groq, OpenAI, or Ollama local |
| **Dashboard** | Google Looker Studio | Native BigQuery integration, interactive filters, free & shareable |

---

## 📁 Project Structure

```
fraud-risk-control-analytics/
├── terraform/                    # Infrastructure as Code (GCS, BigQuery, IAM)
│   ├── main.tf                   # GCS bucket, BigQuery datasets, Service Account, IAM
│   ├── variables.tf              # Input variables: project_id, region, bucket_name
│   ├── outputs.tf                # Outputs: bucket_url, service_account_email
│   └── versions.tf               # Provider versions
├── docs/                         # Documentation & Analysis Reports
│   ├── data_exploration.md       # Comprehensive EDA findings, charts & DW architecture decisions
│   ├── ingestion.md              # Batch ingestion benchmarks, chunking & CLI reference
│   └── airflow_batch_ingest_plan.md # Airflow batch ingestion pipeline specification & execution plan
├── notebooks/                    # Data Profiling & Exploration Notebooks
│   ├── data_exploration.ipynb   # Standardized numerical profiling & schema validation
│   ├── eda_transaction.ipynb     # Transaction distribution exploration
│   ├── eda_identity.ipynb        # Identity & device attribute exploration
│   └── transaction_w_identity.ipynb
├── scripts/                      # Data Ingestion & Utility Scripts
│   ├── ingest_to_gcs.py          # Convert raw CSV to Snappy Parquet & upload to GCS Data Lake
│   └── generate_narration.py     # LLM risk narration generator (TODO)
├── airflow/                      # Batch Workflow Orchestration
│   ├── Dockerfile                # Custom Airflow image with GCP & PyArrow dependencies
│   ├── docker-compose.yaml       # Airflow Webserver, Scheduler & Postgres 16
│   ├── .env.example              # Airflow environment configuration template
│   ├── requirements.txt          # Python dependencies for Airflow
│   └── dags/
│       └── risk_batch_ingest.py  # Automated DAG: CSV -> Parquet -> GCS -> BigQuery External Tables
├── redpanda/                     # Streaming Pipeline (TODO)
│   ├── docker-compose.yaml
│   ├── producer.py
│   └── consumer.py
├── dbt/                          # Data Transformation Layer (TODO)
│   ├── dbt_project.yml
│   ├── models/staging/
│   └── models/marts/
├── looker/                       # Looker Studio Assets (TODO)
│   ├── report_spec.md
│   └── queries/
├── pyproject.toml                # Python dependencies (uv)
├── uv.lock                       # Locked dependency versions
├── Makefile                      # One-command pipeline execution (TODO)
└── README.md
```

---

## 🔧 Quick Start

### Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
- [Terraform](https://developer.hashicorp.com/terraform/install) (>= 1.0)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/tuanpmdev156/fraud-risk-control-analytics.git
cd fraud-risk-control-analytics
uv sync
```

### 2. GCP Authentication

```bash
gcloud auth login
gcloud auth application-default login
```

### 3. Provision Infrastructure

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your GCP project ID and bucket name

terraform init
terraform plan
terraform apply
cd ..
```

### 4. Verify Infrastructure

```bash
terraform -chdir=terraform output
gcloud storage ls
bq ls --project_id=YOUR_PROJECT_ID
```

### 5. Data Exploration & Validation

Inspect distributions, label imbalance, and schema integrity:
- **Notebook**: [`notebooks/data_exploration.ipynb`](notebooks/data_exploration.ipynb) (numerical profiling & memory benchmarks)
- **Report**: [`docs/data_exploration.md`](docs/data_exploration.md) (full visual charts & DW architecture rationale)

```bash
uv run jupyter lab notebooks/data_exploration.ipynb
```

### 6. Ingest Data to GCS Data Lake

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

📖 **Full Ingestion Guide, Benchmarks & CLI Options**: [`docs/ingestion.md`](docs/ingestion.md)

---

### 7. Orchestrate Batch Ingestion with Apache Airflow

The batch ingestion pipeline is fully automated and orchestrated via Apache Airflow, coordinating raw data validation, Parquet conversion, GCS Data Lake ingestion, BigQuery External Table provisioning, and automated Data Quality checks.

#### Pipeline Overview
1. **`check_raw_data`**: Verifies that local raw CSV files exist and are not empty before downstream execution.
2. **`convert_transaction_to_parquet` & `convert_identity_to_parquet`**: Parallel conversion from CSV to Snappy-compressed Parquet (**~88% storage saving**).
3. **`upload_transaction_to_gcs` & `upload_identity_to_gcs`**: Ingests Parquet files into the GCS Data Lake (`gs://<bucket>/raw/ieee_cis/`).
4. **`create_bq_ext_transaction` & `create_bq_ext_identity`**: Automatically provisions BigQuery External Tables in the `raw` dataset pointing directly to Parquet on GCS.
5. **`audit_transaction_data_quality` & `audit_identity_data_quality`**: Automated Data Quality gates validating row counts (**590,540** transactions, **144,233** identities) and verifying primary key integrity (`TransactionID IS NOT NULL`).

#### Quick Commands
```bash
# Start Airflow cluster (Postgres, Webserver, Scheduler)
docker compose -f airflow/docker-compose.yaml up -d --build

# View Airflow Web UI
# URL: http://localhost:8080 (Username: admin | Password: admin)

# Unpause and trigger the DAG via CLI or Web UI
docker compose -f airflow/docker-compose.yaml exec airflow-scheduler airflow dags unpause risk_batch_ingest
docker compose -f airflow/docker-compose.yaml exec airflow-scheduler airflow dags trigger risk_batch_ingest
```

📖 **Full Pipeline Specification & Step-by-Step Plan**: [`docs/airflow_batch_ingest_plan.md`](docs/airflow_batch_ingest_plan.md)
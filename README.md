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

## 2. Dataset

**IEEE-CIS Fraud Detection** (Vesta Corporation) — [Kaggle](https://www.kaggle.com/c/ieee-fraud-detection)
- ~590,540 transactions + ~144,233 identity records
- ~3.5% fraud rate (20,663 labeled fraudulent transactions)
- 400+ features (transaction amount, card type, email domain, device/browser info, etc.)

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
│                                               mart_risk_summary)        │
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
├── terraform/                    # Infrastructure as Code
│   ├── main.tf                   # GCS bucket, BigQuery datasets, Service Account, IAM
│   ├── variables.tf              # Input variables: project_id, region, bucket_name
│   ├── outputs.tf                # Outputs: bucket_url, service_account_email
│   └── versions.tf               # Provider versions
├── airflow/                      # Batch Workflow Orchestration (TODO)
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   └── dags/
│       └── risk_batch_ingest.py
├── redpanda/                     # Streaming Pipeline (TODO)
│   ├── docker-compose.yaml
│   ├── producer.py
│   └── consumer.py
├── dbt/                          # Data Transformation Layer (TODO)
│   ├── dbt_project.yml
│   ├── models/staging/
│   └── models/marts/
├── scripts/                      # Standalone Scripts (TODO)
│   ├── ingest_to_gcs.py
│   └── generate_narration.py
├── looker/                       # Looker Studio Assets (TODO)
│   ├── report_spec.md
│   └── queries/
├── pyproject.toml                # Python dependencies (uv)
├── uv.lock                       # Locked dependency versions
├── Makefile                      # One-command pipeline execution (TODO)
└── README.md
```

---

## 🚀 Current Status

### ✅ Phase 1: Environment Setup & Infrastructure (COMPLETED)

- [x] Python environment with `uv` — dependencies locked (`pyproject.toml` + `uv.lock`)
- [x] Terraform IaC provisioned on GCP:
  - [x] GCS Bucket (Data Lake) with lifecycle policy
  - [x] BigQuery Datasets: `raw`, `staging`, `production`
  - [x] Service Account `pipeline-sa` with IAM roles (`storage.objectAdmin`, `bigquery.dataEditor`, `bigquery.jobUser`)
  - [x] Service Account JSON key auto-generated

### ⬜ Phase 2: Data Ingestion — Batch Pipeline
- [ ] Kaggle API setup & IEEE-CIS dataset download
- [ ] CSV → Parquet conversion script (`scripts/ingest_to_gcs.py`)
- [ ] Airflow DAG orchestration (`airflow/dags/risk_batch_ingest.py`)

### ⬜ Phase 3: Data Transformation with dbt
- [ ] Staging models (`stg_transactions`, `stg_identity`)
- [ ] Fact & Mart models (`fct_transactions`, `mart_risk_summary`, `mart_ai_insights`)
- [ ] Data quality tests

### ⬜ Phase 4: Streaming Pipeline with Redpanda
- [ ] Redpanda broker + Console (Docker)
- [ ] Event Producer & Consumer

### ⬜ Phase 5: Agentic AI Narration Layer
- [ ] LLM integration (provider-agnostic)
- [ ] Anti-hallucination guardrails
- [ ] Write insights to `mart_ai_insights`

### ⬜ Phase 6: Google Looker Studio Dashboard
- [ ] Connect BigQuery data sources
- [ ] Interactive charts, KPI scorecards, AI summary panel

### ⬜ Phase 7: Automation & Testing
- [ ] Makefile with one-command pipeline execution
- [ ] End-to-end pipeline validation

### ⬜ Phase 8: Documentation & Final Review
- [ ] Complete README with reproduction steps
- [ ] Dashboard screenshots & public link

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
```

### 4. Verify Infrastructure

```bash
terraform output
gcloud storage ls
bq ls --project_id=YOUR_PROJECT_ID
```

---

## 📝 License

This project is built for educational purposes as part of the [DataTalksClub Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp).

## 🙏 Acknowledgments

- [DataTalksClub DE Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)
- [IEEE-CIS Fraud Detection Dataset](https://www.kaggle.com/c/ieee-fraud-detection) (Vesta Corporation)
- Reference project: [rayluo88/zoomcamp-dataeng-proj](https://github.com/rayluo88/zoomcamp-dataeng-proj)


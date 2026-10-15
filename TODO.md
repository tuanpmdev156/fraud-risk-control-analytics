# TODO.md

## Project Summary

1. Batch Pipeline: Ingest dữ liệu lịch sử đã có sẵn nhãn (train_transaction.csv đã có nhãn mặt đất isFraud) qua GCS → BigQuery.

2. Transformation (dbt): Xử lý, làm sạch và thống kê tổng hợp các giao dịch đã xảy ra (tỷ lệ gian lận, tổng tiền tổn thất theo loại thẻ, thiết bị, thời gian).

3. Streaming (Redpanda): Replay sự kiện giao dịch vào topic và lưu trữ về BigQuery/GCS (chưa có bước chấm điểm rủi ro qua model).

4. BI Dashboard (Looker Studio): Hiển thị báo cáo giám sát rủi ro (monitoring & descriptive analytics).

5. Agentic AI Layer: Dùng LLM để đọc số liệu aggregate và viết tóm tắt nhận định rủi ro, không phải mô hình ML phân loại nhãn giao dịch.

---

## Phase 1: Environment & Infrastructure Setup (Completed)
- [x] Set up Python environment with `uv` (`pyproject.toml`, `uv.lock`)
- [x] Configure GCP project, Service Account, and IAM roles
- [x] Write and apply Terraform configs (`terraform/`):
  - [x] GCS Bucket (Data Lake)
  - [x] BigQuery Datasets (`raw`, `staging`, `production`)
- [x] Download Kaggle IEEE-CIS Fraud Detection dataset (`data/`)
- [x] Complete preliminary exploratory analysis (`notebooks/`) and document findings in [`docs/data_exploration.md`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/docs/data_exploration.md)

---

## Phase 2: Ingestion & Batch Pipeline (Completed)

- [x] Standardize the exploratory notebook [`notebooks/data_exploration.ipynb`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/notebooks/data_exploration.ipynb) with core distribution charts.
- [x] Develop `scripts/ingest_to_gcs.py`: Convert raw CSV files to Parquet (Snappy compression) and upload to the GCS bucket.
- [x] Author the Airflow DAG `airflow/dags/risk_batch_ingest.py` to automate the batch ingestion pipeline into BigQuery.
- [x] Create external tables in BigQuery `raw` dataset pointing to Parquet files in GCS
- [x] Verify BigQuery table schemas and record counts (590,540 transactions, 144,233 identities)

---

## Phase 3: Data Warehouse & Transformations (dbt)
- [ ] Initialize dbt project (`dbt_fraud_analytics`) with `dbt-bigquery`
- [ ] Implement staging models:
  - [ ] `stg_transaction.sql` (prune to ~20–22 core columns, rename, cast types)
  - [ ] `stg_identity.sql` (standardize column names: replace hyphens with underscores)
- [ ] Implement production marts:
  - [ ] `fct_transactions.sql` (partition by `transaction_date`, cluster by `product_cd`, `card4`, `is_fraud`)
  - [ ] `mart_risk_summary.sql` (aggregated risk metrics by date, card network, device)
- [ ] Add dbt tests (schema validation, `unique`, `not_null`, `accepted_values`)
- [ ] Generate dbt documentation and lineage graph

---

## Phase 4: Streaming Pipeline (Redpanda)
- [ ] Set up Redpanda broker using Docker Compose
- [ ] Develop event producer (`scripts/streaming/producer.py`) to replay transaction events into Kafka topic
- [ ] Develop streaming consumer (`scripts/streaming/consumer.py`) to ingest events into BigQuery / GCS

---

## Phase 5: Agentic AI Narration Layer
- [ ] Develop `scripts/generate_narration.py`:
  - [ ] Query aggregated risk metrics from BigQuery `mart_risk_summary`
  - [ ] Generate structured risk insights using LLM (OpenAI SDK / Groq / DeepSeek)
  - [ ] Insert generated narration into BigQuery table `mart_ai_insights`
- [ ] Integrate narration task into Airflow orchestration DAG

---

## Phase 6: BI Dashboard (Google Looker Studio)
- [ ] Connect Looker Studio to BigQuery production marts (`fct_transactions`, `mart_risk_summary`, `mart_ai_insights`)
- [ ] Build interactive dashboard pages:
  - [ ] Executive KPI scorecards (Total Transaction Volume, Fraud Rate, Fraud Loss Amount)
  - [ ] Risk breakdown charts (by Card Network, Product Code, Device Type, Geo Region)
  - [ ] Hourly Fraud Heatmap (`transaction_hour` vs `day_of_week`)
  - [ ] AI Executive Summary Card (displaying latest LLM-generated narrative insights)

---

## Phase 7: Documentation & Final Polish
- [ ] Finalize end-to-end `README.md` with architecture diagram and reproduction steps
- [ ] Record a 3–5 minute video demo for Zoomcamp peer review
- [ ] Code cleanup, formatting, and final repository verification
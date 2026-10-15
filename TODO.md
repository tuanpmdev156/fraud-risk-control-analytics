# TODO.md

## Project Summary

1. **Batch Pipeline**: Ingest dữ liệu lịch sử đã có sẵn nhãn (`train_transaction.csv` có nhãn `isFraud`) qua GCS → BigQuery External Tables tự động qua Airflow.

2. **Transformation (dbt)**: Xử lý, làm sạch và mô hình hóa Medallion (`stg_*`, `fct_transactions`, `mart_risk_summary`) tối ưu partition & cluster.

3. **Streaming Pipeline (Nâng cấp)**: Replay luồng giao dịch qua Redpanda, tính toán **Sliding Window Features** (vận tốc giao dịch, tần suất quẹt thẻ trong 5-10 phút) và kích hoạt **Instant Alerting qua Telegram Bot** khi chạm ngưỡng rủi ro cao.

4. **BI Dashboard (Looker Studio)**: Hiển thị báo cáo giám sát rủi ro đa chiều (KPIs, Risk breakdown, Hourly Heatmap, AI Incident Report Card).

5. **Agentic AI Layer (Nâng cấp)**: **Agentic Root-Cause Investigator** sử dụng Tool/Function Calling (`execute_bigquery_sql`) để tự động drill-down, truy vấn BigQuery tìm nguyên nhân gốc rễ bất thường và lập bản **Incident Report** hoàn chỉnh.

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

## Phase 4: Streaming Pipeline (Nâng cấp: Real-time Window Features & Alerting)
- [ ] Set up Redpanda broker using Docker Compose
- [ ] Develop event producer (`scripts/streaming/producer.py`) to replay transactions into Kafka topic
- [ ] Develop stream processor / consumer (`scripts/streaming/consumer.py`):
  - [ ] **Sliding Window Processing**: Duy trì state in-memory tính toán window metrics (ví dụ: số giao dịch trong 5 phút `txn_count_5m`, tổng tiền `velocity_amt_5m` theo `card1`)
  - [ ] **Rule-based Risk Engine**: Kiểm tra ngưỡng vi phạm tốc độ quẹt thẻ hoặc số tiền đột biến
  - [ ] **Instant Alerting**: Bắn thông báo cảnh báo tức thì kèm chi tiết giao dịch qua Telegram Bot API / Webhook
  - [ ] Ingest sự kiện luồng vào BigQuery / GCS để phục vụ giám sát

---

## Phase 5: Agentic AI Layer (Nâng cấp: Root-Cause Investigator)
- [ ] Develop `scripts/generate_narration.py` (hoặc `scripts/ai_investigator.py`):
  - [ ] **Anomaly Trigger**: Tự động phát hiện bất thường từ `mart_risk_summary` (tỷ lệ gian lận tăng đột biến > ngưỡng cho phép)
  - [ ] **Function Calling Engine**: Cung cấp tool `execute_bigquery_sql` cho LLM (OpenAI / DeepSeek / Groq)
  - [ ] **ReAct Investigation Loop**: LLM tự động đặt giả thuyết và sinh câu lệnh SQL drill-down vào `fct_transactions` và `stg_identity` (bóc tách theo `card4`, `DeviceType`, `P_emaildomain`, `addr1`)
  - [ ] **Incident Report Generation**: Xuất bản báo cáo chuẩn gồm: Executive Summary, Root-Cause Analysis, Actionable Mitigations và SQL Audit Trail
  - [ ] Ghi báo cáo điều tra vào BigQuery table `mart_ai_insights`
- [ ] Tích hợp task điều tra AI vào Airflow DAG sau khi hoàn thành dbt run

---

## Phase 6: BI Dashboard (Google Looker Studio)
- [ ] Connect Looker Studio to BigQuery production marts (`fct_transactions`, `mart_risk_summary`, `mart_ai_insights`)
- [ ] Build interactive dashboard pages:
  - [ ] Executive KPI scorecards (Total Transaction Volume, Fraud Rate, Fraud Loss Amount)
  - [ ] Risk breakdown charts (by Card Network, Product Code, Device Type, Geo Region)
  - [ ] Hourly Fraud Heatmap (`transaction_hour` vs `day_of_week`)
  - [ ] AI Executive Summary Card (displaying latest LLM-generated narrative insights & Incident Reports)

---

## Phase 7: Documentation & Final Polish
- [ ] Finalize end-to-end `README.md` with architecture diagram and reproduction steps
- [ ] Record a 3–5 minute video demo for Zoomcamp peer review
- [ ] Code cleanup, formatting, and final repository verification
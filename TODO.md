# TODO.md

## Project Summary

1. **Batch Pipeline**: Ingest dữ liệu lịch sử đã có sẵn nhãn (`train_transaction.csv` có nhãn `isFraud`) qua GCS → BigQuery External Tables tự động qua Airflow.

2. **Transformation (dbt)**: Xử lý, làm sạch và mô hình hóa Medallion (`stg_*`, `fct_transactions`, `mart_fraud_summary`) tối ưu partition & cluster.

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
- [ ] **Resilience Testing & Alerting (Mô phỏng sự cố Ingestion & Cảnh báo)**:
  - [x] **Job bị gián đoạn (Job interruption & Idempotency)**: Kích hoạt cờ `SIMULATE_FAILURE = True` trong Airflow DAG; kiểm chứng task retry độc lập và tính Idempotent (ghi đè GCS, `CREATE OR REPLACE EXTERNAL TABLE`).

  - [x] **Cảnh báo lỗi qua Slack (Slack Failure Alerting via `on_failure_callback`)**: Khi task hết số lần retry (`retries exhausted`) và chuyển sang trạng thái `FAILED`, hệ thống phải bắn alert ngay lập tức qua Slack đính kèm link trực tiếp đến Airflow Task Log, Execution Date và DAG ID để kỹ sư on-call truy vết tức thì.
  - [ ] **Schema thay đổi (Schema drift tại nguồn)**: Mô phỏng đổi tên cột hoặc thiếu `TransactionID`; kiểm chứng cơ chế Fail-fast tại PyArrow và `audit_transaction_data_quality`.
---

## Phase 3: Data Warehouse & Transformations (dbt) (Completed)
- [x] Initialize dbt project (`dbt_fraud_risk_control`) with `dbt-bigquery`
- [x] Implement staging models:
  - [x] `stg_transaction.sql` (prune to ~20–22 core columns, rename, cast types)
  - [x] `stg_identity.sql` (standardize column names: replace hyphens with underscores)
- [x] Implement production marts:
  - [x] `fct_transaction.sql` (partition by `transaction_date`, cluster by `product_code`, `card_network`, `is_fraud`)
  - [x] `fraud_risk_summary.sql` (aggregated risk metrics by date, card network, device)
- [x] Add dbt tests (schema validation, `unique`, `not_null`, `accepted_values`, singular tests)
- [x] Generate dbt documentation and lineage graph
- [ ] **Resilience Testing (Mô phỏng sự cố Transformation)**:
  - [ ] **Dữ liệu đến trễ (Late-arriving data)**: Mô phỏng nạp batch ngày cũ ($T-1$, $T-2$); kiểm chứng BigQuery partition (`transaction_date`) tự động định tuyến bản ghi cũ về đúng ngày và thiết lập lookback window cho incremental model.
  - [ ] **Dữ liệu trùng lặp (Duplicates & Deduplication)**: Mô phỏng trùng `transaction_id`; kiểm chứng cảnh báo từ `dbt test` (`unique`) và bổ sung deduplication (`QUALIFY ROW_NUMBER() OVER (...)`) ở `stg_transaction.sql`.
  - [ ] **Dữ liệu không hợp lệ (Invalid data & Quarantine)**: Mô phỏng `transaction_amount <= 0` hoặc nhãn `is_fraud` sai phạm vi; kiểm chứng tests (`assert_positive_amounts`, `assert_valid_fraud_rate`) ngắt pipeline và thiết kế Quarantine Table.

---

## Phase 4: Streaming Pipeline (Nâng cấp: Real-time Window Features & Alerting)
- [ ] Set up Redpanda broker using Docker Compose
- [ ] Develop event producer (`scripts/streaming/producer.py`) to replay transactions into Kafka topic
- [ ] Develop stream processor / consumer (`scripts/streaming/consumer.py`):
  - [ ] **Sliding Window Processing**: Duy trì state in-memory tính toán window metrics (ví dụ: số giao dịch trong 5 phút `txn_count_5m`, tổng tiền `velocity_amt_5m` theo `card1`)
  - [ ] **Rule-based Risk Engine**: Kiểm tra ngưỡng vi phạm tốc độ quẹt thẻ hoặc số tiền đột biến
  - [ ] **Instant Alerting**: Bắn thông báo cảnh báo tức thì kèm chi tiết giao dịch qua Telegram Bot API / Webhook
  - [ ] Ingest sự kiện luồng vào BigQuery / GCS để phục vụ giám sát
  - [ ] **Streaming Resilience**: Xử lý dữ liệu đến trễ (Watermarking cho out-of-order events) và khử trùng lặp sự kiện theo `TransactionID`.

---

## Phase 5: Agentic AI Layer (Nâng cấp: Root-Cause Investigator)
- [ ] Develop `scripts/generate_narration.py` (hoặc `scripts/ai_investigator.py`):
  - [ ] **Anomaly Trigger**: Tự động phát hiện bất thường từ `mart_fraud_summary` (tỷ lệ gian lận tăng đột biến > ngưỡng cho phép)
  - [ ] **Function Calling Engine**: Cung cấp tool `execute_bigquery_sql` cho LLM (OpenAI / DeepSeek / Groq)
  - [ ] **ReAct Investigation Loop**: LLM tự động đặt giả thuyết và sinh câu lệnh SQL drill-down vào `fct_transactions` và `stg_identity` (bóc tách theo `card4`, `DeviceType`, `P_emaildomain`, `addr1`)
  - [ ] **Incident Report Generation**: Xuất bản báo cáo chuẩn gồm: Executive Summary, Root-Cause Analysis, Actionable Mitigations và SQL Audit Trail
  - [ ] Ghi báo cáo điều tra vào BigQuery table `mart_ai_insights`
- [ ] Tích hợp task điều tra AI vào Airflow DAG sau khi hoàn thành dbt run

---

## Phase 6: BI Dashboard (Google Looker Studio)
- [ ] Connect Looker Studio to BigQuery production marts (`fct_transactions`, `mart_fraud_summary`, `mart_ai_insights`)
- [ ] Build interactive dashboard pages:
  - [ ] Executive KPI scorecards (Total Transaction Volume, Fraud Rate, Fraud Loss Amount)
  - [ ] Risk breakdown charts (by Card Network, Product Code, Device Type, Geo Region)
  - [ ] Hourly Fraud Heatmap (`transaction_hour` vs `day_of_week`)
  - [ ] AI Executive Summary Card (displaying latest LLM-generated narrative insights & Incident Reports)

---

## Phase 7: Documentation & Final Polish
- [ ] Finalize end-to-end `README.md` with architecture diagram, reproduction steps, and Resilience & Edge-case handling documentation
- [ ] Record a 3–5 minute video demo for Zoomcamp peer review
- [ ] Code cleanup, formatting, and final repository verification
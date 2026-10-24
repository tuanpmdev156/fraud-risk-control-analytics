# TODO.md

## Project Summary

1. **Batch Pipeline**: Ingest dữ liệu lịch sử đã có sẵn nhãn (`train_transaction.csv` có nhãn `isFraud`) qua GCS → BigQuery External Tables tự động qua Airflow.

2. **Transformation (dbt)**: Xử lý, làm sạch và mô hình hóa Medallion (`stg_*`, `fct_transaction`, `fraud_risk_summary`) tối ưu partition & cluster.

3. **BI Dashboard (Evidence.dev — BI-as-Code)**: Hiển thị báo cáo giám sát rủi ro đa chiều (KPIs, Risk breakdown, Hourly Heatmap).

4. **CI/CD Pipeline (GitHub Actions)**: Tự động hóa kiểm tra chất lượng dữ liệu (`dbt test` / `dbt compile`) và kiểm tra/triển khai hạ tầng (`Terraform`) khi push code hoặc tạo Pull Request.

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
- [x] **Resilience Testing & Alerting (Mô phỏng sự cố Ingestion & Cảnh báo)**:
  - [x] **Job bị gián đoạn (Job interruption & Idempotency)**: Kích hoạt cờ `SIMULATE_FAILURE = True` trong Airflow DAG; kiểm chứng task retry độc lập và tính Idempotent (ghi đè GCS, `CREATE OR REPLACE EXTERNAL TABLE`).

  - [x] **Cảnh báo lỗi qua Slack (Slack Failure Alerting via `on_failure_callback`)**: Khi task hết số lần retry (`retries exhausted`) và chuyển sang trạng thái `FAILED`, hệ thống phải bắn alert ngay lập tức qua Slack đính kèm link trực tiếp đến Airflow Task Log, Execution Date và DAG ID để kỹ sư on-call truy vết tức thì.
  - [x] **Schema thay đổi (Schema drift tại nguồn)**: Mô phỏng đổi tên cột hoặc thiếu `TransactionID`; kiểm chứng cơ chế Fail-fast tại PyArrow và `audit_transaction_data_quality`.
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
- [x] **Resilience Testing (Mô phỏng sự cố Transformation)**:
  - [x] **Dữ liệu trùng lặp (Duplicates & Deduplication)**: Mô phỏng trùng `transaction_id`; kiểm chứng cảnh báo từ `dbt test` (`unique`) và bổ sung deduplication (`QUALIFY ROW_NUMBER() OVER (...)`) ở `stg_transaction.sql`.
  - [x] **Dữ liệu không hợp lệ (Invalid data & Quarantine)**: Mô phỏng `transaction_amount <= 0` hoặc nhãn `is_fraud` sai phạm vi; kiểm chứng tests (`assert_positive_amounts`, `assert_valid_fraud_rate`) ngắt pipeline và thiết kế Quarantine Table.

---

## Phase 4: BI Dashboard (Evidence.dev — BI-as-Code) (Completed)
- [x] Initialize Evidence Studio project ([`evidence/`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence)) and configure [`evidence.config.yaml`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/evidence.config.yaml) & [`theme.yaml`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/theme.yaml)
- [x] Configure BigQuery connection ([`evidence/connection.yaml`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/connection.yaml))
- [x] Write source SQL queries in [`evidence/queries/`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/queries):
  - [x] [`kpi_overview.sql`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/queries/kpi_overview.sql) & [`top_risk_product.sql`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/queries/top_risk_product.sql) (Executive KPI metrics)
  - [x] [`daily.sql`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/queries/daily.sql) & [`fraud_trend.sql`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/queries/fraud_trend.sql) (Daily transaction volume & fraud trends)
  - [x] [`fraud_by_product.sql`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/queries/fraud_by_product.sql), [`fraud_by_card.sql`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/queries/fraud_by_card.sql), [`fraud_by_device.sql`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/queries/fraud_by_device.sql) (Multi-dimensional risk breakdown)
  - [x] [`amount_buckets.sql`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/queries/amount_buckets.sql) (Risk analysis by transaction size)
  - [x] [`narration.sql`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/queries/narration.sql) (AI Insights & executive narration)
- [x] Build unified dashboard in [`evidence/pages/index.md`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/evidence/pages/index.md) (Markdoc + SQL):
  - [x] **Executive Scorecards**: `{% big_value %}` (Total Transactions, Overall Fraud Rate, Fraud Exposure, Highest Risk Product)
  - [x] **Daily Fraud Activity**: `{% combo_chart %}` (Dual-axis transaction volume & fraud count trend)
  - [x] **Fraud Distribution & Profile Breakdown**: `{% horizontal_bar_chart %}` & `{% table %}` (Product Code, Card Network, Device Type)
  - [x] **Risk by Transaction Size**: `{% bar_chart %}` across amount buckets (`micro`, `low`, `medium`, `high`, `critical`)
  - [x] **Data Sources & Inspection**: Detailed interactive `{% table %}` views for underlying datasets
- [ ] Publish / deploy Evidence report (Evidence Studio Cloud / static build)

---

## Phase 5: Documentation & Final Polish
- [ ] Finalize end-to-end `README.md` with architecture diagram, reproduction steps, and Resilience & Edge-case handling documentation
- [ ] Record a 3–5 minute video demo for Zoomcamp peer review
- [ ] Code cleanup, formatting, and final repository verification
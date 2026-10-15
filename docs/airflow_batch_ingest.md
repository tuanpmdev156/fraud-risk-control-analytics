# Hướng Dẫn Pipeline Batch Ingestion với Apache Airflow (Dành Cho Người Mới Bắt Đầu)

> **Mục tiêu**: Đưa dữ liệu giao dịch gian lận (IEEE-CIS Fraud Detection) từ máy cá nhân lên lưu trữ trên Cloud (GCS & BigQuery) một cách hoàn toàn tự động.  
> **Trạng thái**: ✅ **Đã hoàn thành và kiểm thử thành công (100%)**

---

## 1. Bức Tranh Tổng Thể (Dữ liệu đi đâu về đâu?)

Hãy tưởng tượng bạn có 2 file dữ liệu rất lớn trên máy tính (hơn 670 MB file CSV). Để làm việc và phân tích trên Cloud, dữ liệu sẽ đi qua 4 trạm dừng:

```
[1. File CSV trên máy] 
       │ (Nén lại cho nhẹ và chạy nhanh hơn)
       ▼
[2. File Parquet] (Giảm ~75% dung lượng)
       │ (Tải lên Cloud Storage)
       ▼
[3. Google Cloud Storage - Data Lake] (Nơi cất giữ file an toàn)
       │ (Khai báo bảng để có thể truy vấn bằng SQL)
       ▼
[4. Google BigQuery - Data Warehouse] (Nơi phân tích dữ liệu)
```

**Apache Airflow đóng vai trò gì?**  
Airflow giống như một **"Nhạc trưởng tự động"**. Bạn không cần phải mở từng phần mềm bấm chuột bằng tay. Airflow sẽ tự động chạy bước 1, xong bước 1 mới chạy bước 2, nếu lỗi ở đâu thì tự động thử lại hoặc báo cho bạn biết.

---

## 2. Airflow DAG `risk_batch_ingest` Hoạt Động Như Thế Nào?

Toàn bộ quy trình được viết trong 1 file Python duy nhất: [`airflow/dags/risk_batch_ingest.py`](file:///d:/4.DE-zoomcamp/projects/fraud-risk-control-analytics/airflow/dags/risk_batch_ingest.py).

Quy trình gồm **5 bước nhỏ** (tasks):

1. **Bước 1: Kiểm tra file (`check_raw_data`)**
   * Kiểm tra xem 2 file gốc `train_transaction.csv` và `train_identity.csv` đã có trong máy chưa. Nếu thiếu thì dừng ngay để đỡ mất công chạy tiếp.

2. **Bước 2: Nén dữ liệu (`convert_to_parquet`)**
   * Đọc file CSV và chuyển sang định dạng **Parquet** (nén kiểu Snappy).
   * *Tại sao cần bước này?* File CSV cồng kềnh, khi chuyển sang Parquet dung lượng giảm từ 677 MB xuống dưới 100 MB, giúp tải lên mạng nhanh hơn và tiết kiệm tiền lưu trữ trên Google Cloud.

3. **Bước 3: Tải file lên đám mây (`upload_to_gcs`)**
   * Đẩy 2 file Parquet đã nén lên Google Cloud Storage (Bucket: `gs://fraud-risk-131026-data-lake/raw/ieee_cis/`).

4. **Bước 4: Tạo bảng trên BigQuery (`create_bq_external_tables`)**
   * Tạo 2 bảng ngoài (External Tables) trong BigQuery:
     * `raw.ext_transaction`: Chứa dữ liệu giao dịch.
     * `raw.ext_identity`: Chứa thông tin thiết bị/định danh.
   * *Ưu điểm:* BigQuery đọc trực tiếp dữ liệu từ file Parquet trên GCS mà không cần tốn tiền nạp (load) dữ liệu lần hai.

5. **Bước 5: Kiểm tra số lượng dòng (`audit_data_quality`)**
   * Tự động đếm xem số dòng trên BigQuery có khớp với file gốc hay không:
     * Bảng giao dịch: đúng **590,540 dòng**.
     * Bảng định danh: đúng **144,233 dòng**.
     * Cột mã giao dịch (`TransactionID`) không được rỗng (`NULL`).

---

## 3. Cách Bật Và Sử Dụng Airflow (3 Bước Cơ Bản)

Hệ thống Airflow được đóng gói trọn gói trong Docker. Bạn chỉ cần chạy các lệnh sau:

### Bước 1: Khởi động hệ thống
Mở terminal và gõ lệnh:
```bash
docker compose -f airflow/docker-compose.yaml up -d
```
*Lệnh này sẽ khởi động cơ sở dữ liệu Postgres, giao diện Web Airflow và bộ lập lịch Scheduler.*

### Bước 2: Mở giao diện trên trình duyệt
* Mở trình duyệt web và vào địa chỉ: **`http://localhost:8080`**
* Đăng nhập với tài khoản:
  * **Tên đăng nhập (Username)**: `admin`
  * **Mật khẩu (Password)**: `admin`

### Bước 3: Xem và kích hoạt DAG
* Tìm dòng có tên DAG: **`risk_batch_ingest`**.
* Gạt công tắc bên trái từ **Off** sang **On**.
* Bấm nút **Play (Trigger DAG)** ở góc phải để chạy toàn bộ quy trình.
* Nhìn các ô chuyển sang màu **Xanh lá cây (Success)** là hoàn thành!

---

## 4. Những Bài Học Và Lỗi Thường Gặp Cần Lưu Ý

Khi mới làm quen với Docker và Airflow, bạn rất dễ gặp 2 lỗi phổ biến này:

### Lỗi 1: `airflow: command not found` (Không tìm thấy lệnh airflow)
* **Chuyện gì đã xảy ra?** Khi cài đặt thêm thư viện qua file `requirements.txt`, công cụ cài đặt (`pip`) đã tự ý tải phiên bản mới nhất của các gói khác và vô tình **xóa mất** phiên bản Airflow gốc của image.
* **Cách phòng tránh:** Khi viết Dockerfile cho Airflow, luôn dùng cờ `--constraint` để khóa cứng danh sách thư viện tương thích chuẩn từ nhà phát hành Apache Airflow.

### Lỗi 2: Container liên tục bị Restarting (Khởi động lại)
* **Chuyện gì đã xảy ra?** Trong file `docker-compose.yaml`, các container như `airflow-webserver` hay `airflow-scheduler` cần biết cụ thể chúng phải làm gì.
* **Cách phòng tránh:** Luôn chỉ định rõ câu lệnh chạy cho từng service:
  * Cho web: `command: webserver`
  * Cho scheduler: `command: scheduler`

---

## 5. Kết Quả Sau Khi Chạy Xong

Khi chạy xong pipeline này, bạn đã có:
1. **Dữ liệu thô an toàn trên GCS**: Nằm tại `gs://fraud-risk-131026-data-lake/raw/ieee_cis/`.
2. **2 Bảng sẵn sàng truy vấn trên BigQuery**:
   * `fraud-risk-analytics-131026.raw.ext_transaction` (**590,540** giao dịch)
   * `fraud-risk-analytics-131026.raw.ext_identity` (**144,233** thiết bị/danh tính)
3. **Nền tảng sẵn sàng cho Phase 3 (dbt)**: Dữ liệu đã sẵn sàng để làm sạch, biến đổi và tính toán tỷ lệ gian lận.

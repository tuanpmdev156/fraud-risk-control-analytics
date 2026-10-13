# GCS Bucket — Data Lake
resource "google_storage_bucket" "data_lake" {
  name                        = var.gcs_bucket_name
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30 # Auto-delete objects older than 30 days (cost control)
    }
    action {
      type = "Delete"
    }
  }
}


# BigQuery Datasets — Medallion Architecture (Raw → Staging → Production)
resource "google_bigquery_dataset" "raw" {
  dataset_id                 = var.bq_dataset_raw
  friendly_name              = "Raw Data"
  description                = "Raw ingested data from GCS (external tables)"
  location                   = var.region
  delete_contents_on_destroy = true
}

resource "google_bigquery_dataset" "staging" {
  dataset_id                 = var.bq_dataset_staging
  friendly_name              = "Staging Data"
  description                = "Staging layer — dbt views (stg_*)"
  location                   = var.region
  delete_contents_on_destroy = true
}

resource "google_bigquery_dataset" "production" {
  dataset_id                 = var.bq_dataset_production
  friendly_name              = "Production Data"
  description                = "Production marts — fact tables, risk summary, AI insights"
  location                   = var.region
  delete_contents_on_destroy = true
}


# Service Account

resource "google_service_account" "pipeline_sa" {
  account_id   = var.service_account_id
  display_name = "Pipeline Service Account"
  description  = "Service account for batch/streaming pipeline automation"
}

# IAM: GCS Object Admin — full read/write on bucket objects
resource "google_project_iam_member" "pipeline_sa_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

# IAM: BigQuery Data Editor — read/write on BigQuery tables
resource "google_project_iam_member" "pipeline_sa_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

# IAM: BigQuery Job User — permission to run queries/jobs
resource "google_project_iam_member" "pipeline_sa_bigquery_job" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}


# Service Account Key — JSON key for local authentication
resource "google_service_account_key" "pipeline_sa_key" {
  service_account_id = google_service_account.pipeline_sa.name
}

# Save the key to a local file
resource "local_file" "pipeline_sa_key_json" {
  content  = base64decode(google_service_account_key.pipeline_sa_key.private_key)
  filename = "${path.module}/../credentials/pipeline-sa-key.json"

  file_permission = "0600"
}


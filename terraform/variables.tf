variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "gcs_bucket_name" {
  description = "GCS bucket name for Data Lake"
  type        = string
}

variable "bq_dataset_raw" {
  description = "BigQuery dataset for raw data"
  type        = string
  default     = "raw"
}

variable "bq_dataset_staging" {
  description = "BigQuery dataset for staging (dbt views)"
  type        = string
  default     = "staging"
}

variable "bq_dataset_production" {
  description = "BigQuery dataset for production marts"
  type        = string
  default     = "production"
}

variable "service_account_id" {
  description = "Service Account ID for pipeline automation"
  type        = string
  default     = "pipeline-sa"
}


terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Run service
resource "google_cloud_run_service" "ai_edu_backend" {
  name     = "ai-edu-backend"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/ai-edu-backend:latest"

        env {
          name  = "DATABASE_URL"
          value = google_sql_database_instance.postgres.connection_name
        }

        env {
          name  = "FIREBASE_CREDENTIALS_PATH"
          value = "/app/firebase-credentials.json"
        }

        resources {
          limits = {
            cpu    = "2000m"
            memory = "4Gi"
          }
        }
      }

      service_account_name = google_service_account.cloud_run_sa.email
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "100"
        "run.googleapis.com/cpu-throttling" = false
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM service account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run Service Account"
}

# Grant necessary permissions
resource "google_project_iam_member" "cloud_run_sa_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_sa_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Cloud SQL instance
resource "google_sql_database_instance" "postgres" {
  name             = "ai-edu-postgres"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro"

    disk_size = 10

    database_flags {
      name  = "max_connections"
      value = "200"
    }
  }
}

resource "google_sql_database" "ai_edu_db" {
  name     = "ai_edu_db"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "ai_edu_user" {
  name     = "ai_edu_user"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# Variables
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Outputs
output "cloud_run_url" {
  value = google_cloud_run_service.ai_edu_backend.status[0].url
}

output "database_connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}

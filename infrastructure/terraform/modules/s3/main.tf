locals {
  project_suffix = replace(lower(var.gcp_project_id), "_", "-")
}

resource "google_storage_bucket" "results" {
  name                        = "${var.project}-results-${var.environment}-${local.project_suffix}"
  location                    = var.gcp_region
  force_destroy               = var.environment == "dev"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }

    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}

resource "google_storage_bucket" "artifacts" {
  name                        = "${var.project}-artifacts-${var.environment}-${local.project_suffix}"
  location                    = var.gcp_region
  force_destroy               = var.environment == "dev"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }

    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}

resource "google_storage_bucket" "tf_state" {
  count                       = var.create_backend_resources ? 1 : 0
  name                        = "${var.project}-tf-state-${replace(var.gcp_project_id, "_", "-")}"
  location                    = var.gcp_region
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

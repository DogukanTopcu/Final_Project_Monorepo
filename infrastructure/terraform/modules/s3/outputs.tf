output "results_bucket_name" {
  value = google_storage_bucket.results.name
}

output "results_bucket_arn" {
  value = google_storage_bucket.results.url
}

output "artifacts_bucket_name" {
  value = google_storage_bucket.artifacts.name
}

output "artifacts_bucket_arn" {
  value = google_storage_bucket.artifacts.url
}

output "tf_state_bucket_name" {
  value = var.create_backend_resources ? google_storage_bucket.tf_state[0].name : "${var.project}-tf-state-${replace(var.gcp_project_id, "_", "-")}"
}

output "tf_state_bucket_arn" {
  value = var.create_backend_resources ? google_storage_bucket.tf_state[0].url : "gs://${var.project}-tf-state-${replace(var.gcp_project_id, "_", "-")}"
}

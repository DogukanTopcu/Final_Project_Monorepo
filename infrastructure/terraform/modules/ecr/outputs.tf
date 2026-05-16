output "api_repo_url" {
  value = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.api.repository_id}/${google_artifact_registry_repository.api.repository_id}"
}

output "runner_repo_url" {
  value = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${google_artifact_registry_repository.runner.repository_id}/${google_artifact_registry_repository.runner.repository_id}"
}

output "api_repo_arn" {
  value = google_artifact_registry_repository.api.name
}

output "runner_repo_arn" {
  value = google_artifact_registry_repository.runner.name
}

output "registry_host" {
  value = "${var.gcp_region}-docker.pkg.dev"
}

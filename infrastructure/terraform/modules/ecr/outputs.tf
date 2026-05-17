output "api_repo_url" {
  value = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${var.project}-api/${var.project}-api"
}

output "runner_repo_url" {
  value = "${var.gcp_region}-docker.pkg.dev/${var.gcp_project_id}/${var.project}-runner/${var.project}-runner"
}

output "api_repo_arn" {
  value = "projects/${var.gcp_project_id}/locations/${var.gcp_region}/repositories/${var.project}-api"
}

output "runner_repo_arn" {
  value = "projects/${var.gcp_project_id}/locations/${var.gcp_region}/repositories/${var.project}-runner"
}

output "registry_host" {
  value = "${var.gcp_region}-docker.pkg.dev"
}

resource "google_artifact_registry_repository" "api" {
  count         = var.create_repositories ? 1 : 0
  location      = var.gcp_region
  repository_id = "${var.project}-api"
  description   = "Docker repository for thesis API images"
  format        = "DOCKER"
}

resource "google_artifact_registry_repository" "runner" {
  count         = var.create_repositories ? 1 : 0
  location      = var.gcp_region
  repository_id = "${var.project}-runner"
  description   = "Docker repository for thesis runner images"
  format        = "DOCKER"
}

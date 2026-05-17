data "google_project" "current" {
  project_id = var.gcp_project_id
}

resource "google_service_account" "runtime" {
  account_id   = substr("${var.project}-${var.environment}-runtime", 0, 30)
  display_name = "Thesis runtime ${var.environment}"
}

resource "google_service_account" "mlflow" {
  account_id   = substr("${var.project}-${var.environment}-mlflow", 0, 30)
  display_name = "Thesis MLflow ${var.environment}"
}

resource "google_service_account" "github_actions" {
  account_id   = substr("${var.project}-${var.environment}-gha", 0, 30)
  display_name = "Thesis GitHub Actions ${var.environment}"
}

locals {
  runtime_roles = toset([
    "roles/artifactregistry.reader",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectAdmin",
  ])

  mlflow_roles = toset([
    "roles/storage.objectAdmin",
  ])

  github_roles = toset([
    "roles/artifactregistry.reader",
    "roles/artifactregistry.writer",
    "roles/compute.admin",
    "roles/iam.serviceAccountUser",
    "roles/secretmanager.secretAccessor",
    "roles/storage.admin",
  ])

  github_principal        = var.github_repo == "*" ? "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/*" : "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repo}"
  github_repo_is_wildcard = trimspace(var.github_repo) == "*"
}

resource "google_project_iam_member" "runtime" {
  for_each = local.runtime_roles

  project = var.gcp_project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_project_iam_member" "mlflow" {
  for_each = local.mlflow_roles

  project = var.gcp_project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.mlflow.email}"
}

resource "google_project_iam_member" "github_actions" {
  for_each = local.github_roles

  project = var.gcp_project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "${var.project}-${var.environment}-gha-pool"
  display_name              = "GitHub Actions pool ${var.environment}"
}

resource "google_iam_workload_identity_pool_provider" "github" {
  count = var.create_github_oidc && local.github_repo_is_wildcard ? 1 : 0

  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "${var.project}-${var.environment}-gha"
  display_name                       = "GitHub Actions provider ${var.environment}"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  # The Google API rejects an empty attribute_condition for deployment-pipeline
  # providers, so keep a no-op claim check in the wildcard case.
  attribute_condition = "assertion.repository != ''"
}

resource "google_iam_workload_identity_pool_provider" "github_scoped" {
  count = var.create_github_oidc && !local.github_repo_is_wildcard ? 1 : 0

  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "${var.project}-${var.environment}-gha"
  display_name                       = "GitHub Actions provider ${var.environment}"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  attribute_condition = "assertion.repository == '${var.github_repo}'"
}

resource "google_service_account_iam_member" "github_wif" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = local.github_principal
}

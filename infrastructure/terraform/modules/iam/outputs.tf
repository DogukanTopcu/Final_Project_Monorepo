output "ec2_runner_role_arn" {
  value = google_service_account.runtime.email
}

output "ec2_runner_instance_profile_arn" {
  value = google_service_account.runtime.email
}

output "github_actions_role_arn" {
  value = google_service_account.github_actions.email
}

output "mlflow_server_role_arn" {
  value = google_service_account.mlflow.email
}

output "github_actions_workload_identity_provider" {
  value = google_iam_workload_identity_pool_provider.github.name
}

output "sns_topic_arn" {
  value = google_pubsub_topic.alerts.id
}

output "api_log_group" {
  value = "_Default"
}

output "runner_log_group" {
  value = "_Default"
}

output "mlflow_log_group" {
  value = "_Default"
}

output "dashboard_name" {
  value = google_monitoring_dashboard.overview.id
}

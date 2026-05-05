output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "api_log_group" {
  value = aws_cloudwatch_log_group.api.name
}

output "runner_log_group" {
  value = aws_cloudwatch_log_group.runner.name
}

output "mlflow_log_group" {
  value = aws_cloudwatch_log_group.mlflow.name
}

output "dashboard_name" {
  value = aws_cloudwatch_dashboard.overview.dashboard_name
}

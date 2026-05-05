output "ec2_runner_role_arn" {
  value = aws_iam_role.ec2_runner.arn
}

output "ec2_runner_instance_profile_arn" {
  value = aws_iam_instance_profile.ec2_runner.arn
}

output "github_actions_role_arn" {
  value = aws_iam_role.github_actions.arn
}

output "mlflow_server_role_arn" {
  value = aws_iam_role.mlflow_server.arn
}

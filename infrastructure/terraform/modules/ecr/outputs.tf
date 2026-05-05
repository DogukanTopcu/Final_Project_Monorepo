output "api_repo_url" {
  value = aws_ecr_repository.api.repository_url
}

output "runner_repo_url" {
  value = aws_ecr_repository.runner.repository_url
}

output "api_repo_arn" {
  value = aws_ecr_repository.api.arn
}

output "runner_repo_arn" {
  value = aws_ecr_repository.runner.arn
}

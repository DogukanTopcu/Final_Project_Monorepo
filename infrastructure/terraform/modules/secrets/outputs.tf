output "openai_key_arn" {
  value = aws_secretsmanager_secret.openai_key.arn
}

output "together_key_arn" {
  value = aws_secretsmanager_secret.together_key.arn
}

output "hf_token_arn" {
  value = aws_secretsmanager_secret.hf_token.arn
}

output "secret_arns" {
  value = [
    aws_secretsmanager_secret.openai_key.arn,
    aws_secretsmanager_secret.together_key.arn,
    aws_secretsmanager_secret.hf_token.arn,
  ]
}

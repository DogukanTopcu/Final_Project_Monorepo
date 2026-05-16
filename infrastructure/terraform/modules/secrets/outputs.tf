output "kimi_key_arn" {
  value = aws_secretsmanager_secret.kimi_key.arn
}

output "kimi_key_name" {
  value = aws_secretsmanager_secret.kimi_key.name
}

output "openai_compatible_key_arn" {
  value = aws_secretsmanager_secret.openai_compatible_key.arn
}

output "openai_compatible_key_name" {
  value = aws_secretsmanager_secret.openai_compatible_key.name
}

output "hf_token_arn" {
  value = aws_secretsmanager_secret.hf_token.arn
}

output "hf_token_name" {
  value = aws_secretsmanager_secret.hf_token.name
}

output "secret_arns" {
  value = [
    aws_secretsmanager_secret.kimi_key.arn,
    aws_secretsmanager_secret.openai_compatible_key.arn,
    aws_secretsmanager_secret.hf_token.arn,
  ]
}

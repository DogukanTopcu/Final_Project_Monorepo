output "kimi_key_arn" {
  value = try(google_secret_manager_secret.kimi_key[0].id, null)
}

output "kimi_key_name" {
  value = try(google_secret_manager_secret.kimi_key[0].secret_id, null)
}

output "openai_compatible_key_arn" {
  value = try(google_secret_manager_secret.openai_compatible_key[0].id, null)
}

output "openai_compatible_key_name" {
  value = try(google_secret_manager_secret.openai_compatible_key[0].secret_id, null)
}

output "hf_token_arn" {
  value = try(google_secret_manager_secret.hf_token[0].id, null)
}

output "hf_token_name" {
  value = "${var.project}-hf-token"
}

output "secret_arns" {
  value = compact([
    try(google_secret_manager_secret.kimi_key[0].id, null),
    try(google_secret_manager_secret.openai_compatible_key[0].id, null),
    try(google_secret_manager_secret.hf_token[0].id, null),
  ])
}

output "kimi_key_arn" {
  value = google_secret_manager_secret.kimi_key.id
}

output "kimi_key_name" {
  value = google_secret_manager_secret.kimi_key.secret_id
}

output "openai_compatible_key_arn" {
  value = google_secret_manager_secret.openai_compatible_key.id
}

output "openai_compatible_key_name" {
  value = google_secret_manager_secret.openai_compatible_key.secret_id
}

output "hf_token_arn" {
  value = google_secret_manager_secret.hf_token.id
}

output "hf_token_name" {
  value = google_secret_manager_secret.hf_token.secret_id
}

output "secret_arns" {
  value = [
    google_secret_manager_secret.kimi_key.id,
    google_secret_manager_secret.openai_compatible_key.id,
    google_secret_manager_secret.hf_token.id,
  ]
}

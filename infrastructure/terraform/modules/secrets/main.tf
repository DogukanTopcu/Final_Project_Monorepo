resource "google_secret_manager_secret" "kimi_key" {
  secret_id = "${var.project}-kimi-api-key"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "openai_compatible_key" {
  secret_id = "${var.project}-openai-compatible-api-key"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "hf_token" {
  secret_id = "${var.project}-hf-token"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "kimi_key" {
  secret      = google_secret_manager_secret.kimi_key.id
  secret_data = jsonencode({ KIMI_API_KEY = "REPLACE_ME" })

  lifecycle {
    ignore_changes = [secret_data]
  }
}

resource "google_secret_manager_secret_version" "openai_compatible_key" {
  secret      = google_secret_manager_secret.openai_compatible_key.id
  secret_data = jsonencode({ OPENAI_COMPATIBLE_API_KEY = "REPLACE_ME" })

  lifecycle {
    ignore_changes = [secret_data]
  }
}

resource "google_secret_manager_secret_version" "hf_token" {
  secret      = google_secret_manager_secret.hf_token.id
  secret_data = jsonencode({ HF_TOKEN = "REPLACE_ME" })

  lifecycle {
    ignore_changes = [secret_data]
  }
}

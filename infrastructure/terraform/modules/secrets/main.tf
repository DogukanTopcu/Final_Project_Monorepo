resource "aws_secretsmanager_secret" "kimi_key" {
  name        = "${var.project}/kimi-api-key"
  description = "Optional Kimi API key for thesis experiments"

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret" "openai_compatible_key" {
  name        = "${var.project}/openai-compatible-api-key"
  description = "Optional OpenAI-compatible gateway key for hosted thesis experiments"

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret" "hf_token" {
  name        = "${var.project}/hf-token"
  description = "Hugging Face token for thesis experiments"

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "kimi_key" {
  secret_id     = aws_secretsmanager_secret.kimi_key.id
  secret_string = "{\"KIMI_API_KEY\": \"REPLACE_ME\"}"

  lifecycle {
    ignore_changes = [secret_string]
  }
}

resource "aws_secretsmanager_secret_version" "openai_compatible_key" {
  secret_id     = aws_secretsmanager_secret.openai_compatible_key.id
  secret_string = "{\"OPENAI_COMPATIBLE_API_KEY\": \"REPLACE_ME\"}"

  lifecycle {
    ignore_changes = [secret_string]
  }
}

resource "aws_secretsmanager_secret_version" "hf_token" {
  secret_id     = aws_secretsmanager_secret.hf_token.id
  secret_string = "{\"HF_TOKEN\": \"REPLACE_ME\"}"

  lifecycle {
    ignore_changes = [secret_string]
  }
}

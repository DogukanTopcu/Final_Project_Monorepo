resource "aws_secretsmanager_secret" "openai_key" {
  name        = "${var.project}/openai-api-key"
  description = "OpenAI API key for thesis experiments"

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret" "together_key" {
  name        = "${var.project}/together-api-key"
  description = "Together AI API key for thesis experiments"

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

resource "aws_secretsmanager_secret_version" "openai_key" {
  secret_id     = aws_secretsmanager_secret.openai_key.id
  secret_string = "{\"OPENAI_API_KEY\": \"REPLACE_ME\"}"

  lifecycle {
    ignore_changes = [secret_string]
  }
}

resource "aws_secretsmanager_secret_version" "together_key" {
  secret_id     = aws_secretsmanager_secret.together_key.id
  secret_string = "{\"TOGETHER_API_KEY\": \"REPLACE_ME\"}"

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

resource "aws_dynamodb_table" "experiments" {
  name         = "${var.project}-experiments"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "experiment_id"
  range_key    = "timestamp"

  attribute {
    name = "experiment_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "architecture"
    type = "S"
  }

  global_secondary_index {
    name            = "architecture-index"
    hash_key        = "architecture"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_dynamodb_table" "tf_lock" {
  count        = var.create_backend_lock_table ? 1 : 0
  name         = "${var.project}-tf-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

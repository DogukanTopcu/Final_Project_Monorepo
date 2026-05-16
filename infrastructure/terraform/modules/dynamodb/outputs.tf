output "experiments_table_name" {
  value = aws_dynamodb_table.experiments.name
}

output "experiments_table_arn" {
  value = aws_dynamodb_table.experiments.arn
}

output "tf_lock_table_name" {
  value = var.create_backend_lock_table ? aws_dynamodb_table.tf_lock[0].name : "${var.project}-tf-lock"
}

output "tf_lock_table_arn" {
  value = var.create_backend_lock_table ? aws_dynamodb_table.tf_lock[0].arn : null
}

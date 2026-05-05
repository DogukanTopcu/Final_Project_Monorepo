output "experiments_table_name" {
  value = aws_dynamodb_table.experiments.name
}

output "experiments_table_arn" {
  value = aws_dynamodb_table.experiments.arn
}

output "tf_lock_table_name" {
  value = aws_dynamodb_table.tf_lock.name
}

output "tf_lock_table_arn" {
  value = aws_dynamodb_table.tf_lock.arn
}

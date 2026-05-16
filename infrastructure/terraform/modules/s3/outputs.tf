output "results_bucket_name" {
  value = aws_s3_bucket.results.bucket
}

output "results_bucket_arn" {
  value = aws_s3_bucket.results.arn
}

output "artifacts_bucket_name" {
  value = aws_s3_bucket.artifacts.bucket
}

output "artifacts_bucket_arn" {
  value = aws_s3_bucket.artifacts.arn
}

output "tf_state_bucket_name" {
  value = var.create_backend_resources ? aws_s3_bucket.tf_state[0].bucket : "${var.project}-tf-state"
}

output "tf_state_bucket_arn" {
  value = var.create_backend_resources ? aws_s3_bucket.tf_state[0].arn : "arn:aws:s3:::${var.project}-tf-state"
}

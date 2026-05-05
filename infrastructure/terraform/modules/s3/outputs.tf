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
  value = aws_s3_bucket.tf_state.bucket
}

output "tf_state_bucket_arn" {
  value = aws_s3_bucket.tf_state.arn
}

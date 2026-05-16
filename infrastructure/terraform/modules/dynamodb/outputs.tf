output "experiments_table_name" {
  value = local.experiments_collection
}

output "experiments_table_arn" {
  value = "firestore://${local.experiments_collection}"
}

output "tf_lock_table_name" {
  value = ""
}

output "tf_lock_table_arn" {
  value = null
}

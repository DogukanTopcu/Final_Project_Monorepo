output "vpc_id" {
  value = google_compute_network.main.id
}

output "public_subnet_ids" {
  value = google_compute_subnetwork.public[*].self_link
}

output "private_subnet_ids" {
  value = google_compute_subnetwork.private[*].self_link
}

output "vpc_cidr" {
  value = var.vpc_cidr
}

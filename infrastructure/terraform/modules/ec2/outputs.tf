output "instance_ids" {
  value = google_compute_instance.runner[*].instance_id
}

output "public_ips" {
  value = [
    for inst in google_compute_instance.runner :
    try(inst.network_interface[0].access_config[0].nat_ip, null)
  ]
}

output "private_ips" {
  value = [for inst in google_compute_instance.runner : inst.network_interface[0].network_ip]
}

output "security_group_id" {
  value = google_compute_firewall.ssh.name
}

output "ssh_commands" {
  value = [
    for inst in google_compute_instance.runner :
    "ssh -i ~/.ssh/thesis-key ${var.ssh_username}@${try(inst.network_interface[0].access_config[0].nat_ip, inst.network_interface[0].network_ip)}"
  ]
}

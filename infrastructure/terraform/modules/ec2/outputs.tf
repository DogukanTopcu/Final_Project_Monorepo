output "instance_ids" {
  value = aws_instance.runner[*].id
}

output "public_ips" {
  value = aws_instance.runner[*].public_ip
}

output "private_ips" {
  value = aws_instance.runner[*].private_ip
}

output "security_group_id" {
  value = aws_security_group.runner.id
}

output "ssh_commands" {
  value = [
    for inst in aws_instance.runner :
    "ssh -i ~/.ssh/thesis-key.pem ec2-user@${inst.public_ip}"
  ]
}

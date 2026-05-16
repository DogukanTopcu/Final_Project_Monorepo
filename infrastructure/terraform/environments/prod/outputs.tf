output "api_public_ip" {
  value = try(module.ec2_cpu.public_ips[0], null)
}

output "api_private_ip" {
  value = try(module.ec2_cpu.private_ips[0], null)
}

output "vllm_private_endpoints" {
  value = {
    for model_id, host in module.vllm_hosts :
    model_id => "http://${host.private_ips[0]}:8000/v1"
  }
}

output "vllm_instance_ids" {
  value = {
    for model_id, host in module.vllm_hosts :
    model_id => host.instance_ids[0]
  }
}

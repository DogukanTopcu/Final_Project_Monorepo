#!/bin/bash
set -euo pipefail

yum update -y
yum install -y docker aws-cli jq
systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

%{ if is_gpu }
yum install -y nvidia-container-toolkit
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker
%{ endif }

%{ if ecr_repo_url != "" }
aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin ${ecr_repo_url}
%{ endif }

docker pull ${container_image_uri}

mkdir -p /etc/thesis
: > /etc/thesis/.env
%{ for secret_name in secret_names ~}
aws secretsmanager get-secret-value \
  --secret-id ${secret_name} \
  --region ${aws_region} \
  --query SecretString \
  --output text | jq -r 'to_entries[] | "\(.key)=\(.value)"' >> /etc/thesis/.env
%{ endfor ~}

if grep -q '^HF_TOKEN=' /etc/thesis/.env && ! grep -q '^HUGGING_FACE_HUB_TOKEN=' /etc/thesis/.env; then
  HF_VALUE="$(grep '^HF_TOKEN=' /etc/thesis/.env | tail -n 1 | cut -d= -f2-)"
  echo "HUGGING_FACE_HUB_TOKEN=$${HF_VALUE}" >> /etc/thesis/.env
fi

cat >> /etc/thesis/.env <<ENVEOF
MLFLOW_TRACKING_URI=http://localhost:5000
ENVIRONMENT=${environment}
%{ for key, value in extra_env ~}
${key}=${value}
%{ endfor ~}
ENVEOF

docker run -d \
  --name ${container_name} \
  --env-file /etc/thesis/.env \
  --restart unless-stopped \
  %{ for port_mapping in port_mappings ~}
  -p ${port_mapping} \
  %{ endfor ~}
  %{ for runtime_arg in container_runtime_args ~}
  ${runtime_arg} \
  %{ endfor ~}
  %{ if is_gpu }--gpus all%{ endif } \
  ${container_image_uri}%{ if container_command != "" } \
  ${container_command}%{ endif }

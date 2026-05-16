#!/bin/bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y ca-certificates curl docker.io jq python3 python3-pip
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu || true

%{ if is_gpu }
if ! command -v nvidia-ctk >/dev/null 2>&1; then
  distribution=$(. /etc/os-release; echo $${ID}$${VERSION_ID})
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  curl -fsSL https://nvidia.github.io/libnvidia-container/$${distribution}/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' > /etc/apt/sources.list.d/nvidia-container-toolkit.list
  apt-get update
  apt-get install -y nvidia-container-toolkit
  nvidia-ctk runtime configure --runtime=docker
  systemctl restart docker
fi
%{ endif }

METADATA_HEADER="Metadata-Flavor: Google"
ACCESS_TOKEN="$(curl -fsSL -H "$${METADATA_HEADER}" http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token | jq -r '.access_token')"

echo "$${ACCESS_TOKEN}" | docker login -u oauth2accesstoken --password-stdin https://${artifact_registry_host}
docker pull ${container_image_uri}

mkdir -p /etc/thesis
: > /etc/thesis/.env
%{ for secret_name in secret_names ~}
curl -fsSL \
  -H "Authorization: Bearer $${ACCESS_TOKEN}" \
  "https://secretmanager.googleapis.com/v1/projects/${gcp_project_id}/secrets/${secret_name}/versions/latest:access" | \
  jq -r '.payload.data' | base64 --decode | \
  jq -r 'to_entries[] | "\(.key)=\(.value)"' >> /etc/thesis/.env
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

docker rm -f ${container_name} >/dev/null 2>&1 || true
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

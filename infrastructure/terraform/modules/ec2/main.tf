data "google_compute_image" "selected" {
  family  = var.is_gpu ? var.gpu_source_image_family : var.cpu_source_image_family
  project = var.is_gpu ? var.gpu_source_image_project : var.cpu_source_image_project
}

locals {
  instance_tag = replace("${var.project}-${var.environment}", ".", "-")
}

resource "google_compute_firewall" "ssh" {
  name    = "${local.instance_tag}-ssh"
  network = var.vpc_id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = [var.allowed_ssh_cidr]
  target_tags   = [local.instance_tag]
}

resource "google_compute_firewall" "api" {
  count   = length(var.api_ingress_cidrs) > 0 ? 1 : 0
  name    = "${local.instance_tag}-api"
  network = var.vpc_id

  allow {
    protocol = "tcp"
    ports    = [tostring(var.api_port)]
  }

  source_ranges = var.api_ingress_cidrs
  target_tags   = [local.instance_tag]
}

resource "google_compute_instance" "runner" {
  count        = var.instance_count
  name         = "${local.instance_tag}-${count.index}"
  machine_type = var.instance_type
  zone         = var.gcp_zone
  tags         = [local.instance_tag]

  labels = {
    project     = var.project
    environment = replace(var.environment, ".", "-")
    workload    = replace(var.container_name, "_", "-")
    name        = replace("${var.project}-runner-${count.index}-${var.environment}", ".", "-")
  }

  boot_disk {
    auto_delete = true

    initialize_params {
      image = data.google_compute_image.selected.self_link
      size  = var.root_volume_size_gb
      type  = var.root_volume_type
    }
  }

  network_interface {
    subnetwork = var.subnet_id

    dynamic "access_config" {
      for_each = var.assign_public_ip ? [1] : []
      content {}
    }
  }

  metadata = {
    ssh-keys = "${var.ssh_username}:${file(var.public_key_path)}"
  }

  metadata_startup_script = templatefile("${path.module}/user_data.sh", {
    artifact_registry_host = var.artifact_registry_host
    container_image_uri    = var.container_image_uri
    container_name         = var.container_name
    container_runtime_args = var.container_runtime_args
    container_command      = var.container_command
    environment            = var.environment
    extra_env              = var.extra_env
    gcp_project_id         = var.gcp_project_id
    is_gpu                 = var.is_gpu
    port_mappings          = var.port_mappings
    secret_names           = var.secret_names
  })

  scheduling {
    automatic_restart   = var.use_spot ? false : true
    on_host_maintenance = var.is_gpu ? "TERMINATE" : "MIGRATE"
    preemptible         = var.use_spot
    provisioning_model  = var.use_spot ? "SPOT" : "STANDARD"
  }

  service_account {
    email  = var.service_account_email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

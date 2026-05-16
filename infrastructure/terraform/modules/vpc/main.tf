resource "google_compute_network" "main" {
  name                    = "${var.project}-vpc-${var.environment}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "public" {
  count = length(var.public_subnet_cidrs)

  name                     = "${var.project}-public-${count.index}-${var.environment}"
  ip_cidr_range            = var.public_subnet_cidrs[count.index]
  region                   = var.gcp_region
  network                  = google_compute_network.main.id
  private_ip_google_access = true
}

resource "google_compute_subnetwork" "private" {
  count = length(var.private_subnet_cidrs)

  name                     = "${var.project}-private-${count.index}-${var.environment}"
  ip_cidr_range            = var.private_subnet_cidrs[count.index]
  region                   = var.gcp_region
  network                  = google_compute_network.main.id
  private_ip_google_access = true
}

resource "google_compute_router" "main" {
  count   = var.nat_enabled ? 1 : 0
  name    = "${var.project}-router-${var.environment}"
  region  = var.gcp_region
  network = google_compute_network.main.id
}

resource "google_compute_router_nat" "main" {
  count  = var.nat_enabled ? 1 : 0
  name   = "${var.project}-nat-${var.environment}"
  router = google_compute_router.main[0].name
  region = var.gcp_region

  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"

  dynamic "subnetwork" {
    for_each = google_compute_subnetwork.private
    content {
      name                    = subnetwork.value.id
      source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
    }
  }
}

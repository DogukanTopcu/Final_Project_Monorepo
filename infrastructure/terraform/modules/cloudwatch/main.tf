resource "google_pubsub_topic" "alerts" {
  name = "${var.project}-alerts-${var.environment}"
}

resource "google_monitoring_notification_channel" "email" {
  count        = var.alert_email != "" ? 1 : 0
  display_name = "${var.project}-${var.environment}-email"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }
}

resource "google_monitoring_alert_policy" "cpu" {
  count        = length(var.instance_ids)
  display_name = "${var.project}-cpu-high-${count.index}-${var.environment}"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "High CPU on instance ${count.index}"

    condition_threshold {
      comparison      = "COMPARISON_GT"
      duration        = "300s"
      threshold_value = 0.85
      filter          = "metric.type=\"compute.googleapis.com/instance/cpu/utilization\" AND resource.type=\"gce_instance\" AND resource.label.\"instance_id\"=\"${var.instance_ids[count.index]}\""

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_MEAN"
        cross_series_reducer = "REDUCE_NONE"
      }
    }
  }

  notification_channels = var.alert_email != "" ? [google_monitoring_notification_channel.email[0].name] : []
}

resource "google_monitoring_dashboard" "overview" {
  dashboard_json = jsonencode({
    displayName = "${var.project}-overview-${var.environment}"
    mosaicLayout = {
      columns = 12
      tiles = [
        for i, id in var.instance_ids : {
          xPos   = 0
          yPos   = i * 4
          width  = 12
          height = 4
          widget = {
            title = "CPU utilization ${i}"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"compute.googleapis.com/instance/cpu/utilization\" AND resource.type=\"gce_instance\" AND resource.label.\"instance_id\"=\"${id}\""
                    aggregation = {
                      alignmentPeriod    = "300s"
                      perSeriesAligner   = "ALIGN_MEAN"
                      crossSeriesReducer = "REDUCE_NONE"
                    }
                  }
                }
              }]
            }
          }
        }
      ]
    }
  })
}

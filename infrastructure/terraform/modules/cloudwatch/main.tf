resource "aws_cloudwatch_log_group" "api" {
  name              = "/${var.project}/api"
  retention_in_days = 30

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "runner" {
  name              = "/${var.project}/runner"
  retention_in_days = 30

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "mlflow" {
  name              = "/${var.project}/mlflow"
  retention_in_days = 30

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_sns_topic" "alerts" {
  name = "${var.project}-alerts-${var.environment}"

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

resource "aws_cloudwatch_metric_alarm" "cost" {
  alarm_name          = "${var.project}-daily-cost-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 86400
  statistic           = "Maximum"
  threshold           = var.cost_threshold
  alarm_description   = "Daily estimated cost exceeds $${var.cost_threshold}"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    Currency = "USD"
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_cloudwatch_metric_alarm" "cpu" {
  count               = length(var.instance_ids)
  alarm_name          = "${var.project}-cpu-high-${count.index}-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "EC2 CPU > 85% for 5 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = var.instance_ids[count.index]
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_cloudwatch_dashboard" "overview" {
  dashboard_name = "${var.project}-overview-${var.environment}"

  dashboard_body = jsonencode({
    widgets = concat(
      [for i, id in var.instance_ids : {
        type   = "metric"
        x      = (i % 2) * 12
        y      = (floor(i / 2)) * 6
        width  = 12
        height = 6
        properties = {
          title   = "CPU/Memory - Instance ${i}"
          metrics = [
            ["AWS/EC2", "CPUUtilization", "InstanceId", id],
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
        }
      }],
      [{
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 6
        properties = {
          title   = "S3 Storage"
          metrics = [
            ["AWS/S3", "BucketSizeBytes", "BucketName", var.results_bucket, "StorageType", "StandardStorage"],
          ]
          period = 86400
          stat   = "Average"
          region = var.aws_region
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 12
        width  = 12
        height = 6
        properties = {
          title   = "DynamoDB Read/Write"
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", var.dynamodb_table],
            ["AWS/DynamoDB", "ConsumedWriteCapacityUnits", "TableName", var.dynamodb_table],
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
        }
      }]
    )
  })
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_security_group" "runner" {
  name_prefix = "${var.project}-runner-${var.environment}-"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH from allowed CIDR"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  dynamic "ingress" {
    for_each = length(var.api_ingress_cidrs) > 0 ? [1] : []
    content {
      description = "Application access"
      from_port   = var.api_port
      to_port     = var.api_port
      protocol    = "tcp"
      cidr_blocks = var.api_ingress_cidrs
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project}-runner-sg-${var.environment}"
    Project     = var.project
    Environment = var.environment
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_key_pair" "runner" {
  key_name   = "${var.project}-runner-${var.environment}"
  public_key = file(var.public_key_path)

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_launch_template" "runner" {
  name_prefix   = "${var.project}-runner-${var.environment}-"
  image_id      = var.ami_id != "" ? var.ami_id : data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.runner.key_name

  iam_instance_profile {
    arn = var.instance_profile_arn
  }

  vpc_security_group_ids = [aws_security_group.runner.id]

  block_device_mappings {
    device_name = "/dev/xvda"

    ebs {
      volume_size           = var.root_volume_size_gb
      volume_type           = var.root_volume_type
      delete_on_termination = true
    }
  }

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    ecr_repo_url           = var.ecr_repo_url
    aws_region             = var.aws_region
    secret_names           = var.secret_names
    environment            = var.environment
    is_gpu                 = var.is_gpu
    container_image_uri    = var.container_image_uri
    container_name         = var.container_name
    port_mappings          = var.port_mappings
    container_runtime_args = var.container_runtime_args
    container_command      = var.container_command
    extra_env              = var.extra_env
  }))

  dynamic "instance_market_options" {
    for_each = var.use_spot ? [1] : []
    content {
      market_type = "spot"
      spot_options {
        max_price = var.spot_price
      }
    }
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name        = "${var.project}-runner-${var.environment}"
      Project     = var.project
      Environment = var.environment
    }
  }

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

resource "aws_instance" "runner" {
  count = var.instance_count

  launch_template {
    id      = aws_launch_template.runner.id
    version = "$Latest"
  }

  subnet_id = var.subnet_id

  tags = {
    Name        = "${var.project}-runner-${count.index}-${var.environment}"
    Project     = var.project
    Environment = var.environment
  }
}

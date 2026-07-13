# ─────────────────────────────────────────
# ECR Repository (existing)
# ─────────────────────────────────────────
resource "aws_ecr_repository" "dialysisbot" {
  name                 = var.project_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }

  tags = {
    Name    = var.project_name
    Project = var.project_name
  }

  lifecycle {
    ignore_changes = all
  }
}

# ─────────────────────────────────────────
# Security Group (existing)
# ─────────────────────────────────────────
resource "aws_security_group" "jenkins_sg" {
  name        = "${var.project_name}-jenkins-sg"
  description = "Security group for Jenkins server"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Jenkins UI"
  }

  ingress {
    from_port   = 50000
    to_port     = 50000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Jenkins agent"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name    = "${var.project_name}-jenkins-sg"
    Project = var.project_name
  }

  lifecycle {
    ignore_changes = all
  }
}

# ─────────────────────────────────────────
# EC2 Instance (existing)
# ─────────────────────────────────────────
resource "aws_instance" "jenkins" {
  ami                    = "ami-01a00762f46d584a1"
  instance_type          = "c7i-flex.large"
  key_name               = "dialysisbot-key"
  vpc_security_group_ids = ["sg-0e047c70393fce2ed"]

  tags = {
    Name    = "${var.project_name}-jenkins"
    Project = var.project_name
  }

  lifecycle {
    ignore_changes = all
  }
}

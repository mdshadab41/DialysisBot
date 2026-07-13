# aws region
variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-south-1"

}

# project name
variable "project_name" {
  description = "Project name used for naming resources"
  type        = string
  default     = "dialysisbot"

}

# ec2 instance type
variable "instance_type" {
  description = "EC2 instance type for Jenkins"
  type        = string
  default     = "c7i-flex.large"
}
# your ip for SSH access
variable "my_ip" {
  description = "Your local IP for SSH access"
  type        = string
  default     = "0.0.0.0/0"
}

# ec2 key pair name
variable "key_pair_name" {
  description = "EC2 key pair name for SSH access"
  type        = string
  default     = "dialysisbot-key"

}


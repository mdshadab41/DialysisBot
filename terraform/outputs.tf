# EC2 Public IP
output "jenkins_public_ip" {
  description = "Public IP of Jenkins EC2 instance"
  value       = aws_instance.jenkins.public_ip
}

# EC2 Instance ID
output "jenkins_instance_id" {
  description = "Instance ID of Jenkins EC2"
  value       = aws_instance.jenkins.id
}

# ECR Repository URL
output "ecr_repository_url" {
  description = "ECR repository URL for Docker push"
  value       = aws_ecr_repository.dialysisbot.repository_url
}

# SSH Command
output "ssh_command" {
  description = "SSH command to connect to Jenkins"
  value       = "ssh -i ${var.key_pair_name}.pem ubuntu@${aws_instance.jenkins.public_ip}"
}

# Jenkins URL
output "jenkins_url" {
  description = "Jenkins URL"
  value       = "http://${aws_instance.jenkins.public_ip}:8080"
}

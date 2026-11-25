resource "aws_security_group" "demo_open_ssh" {
  name        = "demo-open-ssh"
  description = "Deliberately insecure group for the failing scan demo"

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
} 
# Latest Ubuntu 24.04 LTS from Canonical. Ansible (Part 2) uses apt,
# so this has to stay a Debian/Ubuntu image.
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

resource "aws_key_pair" "this" {
  key_name   = "${var.name}-key"
  public_key = var.ssh_public_key

  tags = {
    Name = "${var.name}-key"
  }
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = var.security_group_ids
  key_name                    = aws_key_pair.this.key_name
  associate_public_ip_address = true
  ebs_optimized               = true
  monitoring                  = false # detailed monitoring is not free tier

  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    hostname = "${var.name}-app"
  })

  # IMDSv2 only, stops SSRF style token theft from the metadata service
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_size
    encrypted             = true
    delete_on_termination = true

    tags = {
      Name = "${var.name}-app-root"
    }
  }

  # Ansible's aws_ec2 inventory groups hosts by these tags
  tags = merge(var.instance_tags, {
    Name = "${var.name}-app"
    Role = "app"
  })

  lifecycle {
    # A new Ubuntu AMI shouldn't force a rebuild of a running server
    ignore_changes = [ami]
  }
}

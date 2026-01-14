resource "aws_instance" "ioana-vm" {
  ami                    = var.ami_id
  instance_type          = "t3.micro"
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  key_name               = var.key_name

  associate_public_ip_address = true

# helpful for Ansible
  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y python3 python3-apt
              EOF

  tags = {
    Name = "${var.project}"
  }
}


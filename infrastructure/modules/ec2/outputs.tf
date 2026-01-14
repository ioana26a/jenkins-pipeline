output "ec2_public_ip" {
    value = aws_instance.ioana-vm.public_ip
}
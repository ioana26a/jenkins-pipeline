variable "aws_region" {
  type = string
}
variable "key_name" {
  type = string
}
variable "project" {
  type = string
}
variable "instance_type" {
  type = string
}
variable "ami_id" {
  type = string
}
variable "vpc_id" {
  type = string
}
variable "subnet_id" {
  type = string
}
variable "allowed_ip" {
  description = "Allowed IP address for SSH access in CIDR notation (e.g., 203.0.113.1/32)"
  type        = list(string)
}
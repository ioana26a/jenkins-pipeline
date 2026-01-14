# Jenkins Pipeline Project

This project demonstrates a complete CI/CD workflow using **Jenkins Pipeline** to build, test, containerize, and deploy a Python Flask application with a MariaDB backend and NGINX frontend. The infrastructure is managed using **Terraform** (for AWS EC2 provisioning) and **Ansible** (for server configuration).

---

## Project Structure

- **app/**: Flask API, NGINX config, Dockerfile, and database initialization scripts.
- **infrastructure/**:
  - **modules/ec2/**: Terraform code for AWS EC2 provisioning.
  - **ansible/**: Playbooks and roles for configuring Docker and AWS CLI on EC2.

---

## Jenkins Pipeline Overview

The Jenkins pipeline (`Jenkinsfile`) automates the following steps:

1. **Checkout Source Code**
   Clones the application and infrastructure code from a Git repository.

2. **Test and Lint**
   - Sets up a Python virtual environment.
   - Installs dependencies.
   - Runs unit tests (`pytest`) and code linting (`flake8`).

3. **Build and Tag Docker Image**
   - Builds the Docker image using `docker-compose`.
   - Tags the image with the build version and for AWS ECR.

4. **Push to AWS ECR**
   - Authenticates with AWS ECR.
   - Pushes the Docker image to the ECR repository.

5. **Deploy to EC2**
   - Connects to the provisioned EC2 instance via SSH.
   - Installs Docker and AWS CLI if missing (using Ansible or shell commands).
   - Pulls the latest Docker image from ECR.
   - Runs the container, handling port switching for zero-downtime deployment.
   - Cleans up old containers.

6. **Validation**
   - Verifies the application is running and accessible on the EC2 instance.

---

## Purpose

- **Automate** the build, test, and deployment process for a Flask web application.
- **Provision** and configure AWS infrastructure using Infrastructure as Code (Terraform & Ansible).
- **Ensure** reliable, repeatable deployments with minimal manual intervention.

---

## Getting Started

### Prerequisites

- Jenkins server with required plugins (Pipeline, Docker, AWS, SSH Agent).
- AWS account with ECR and EC2 permissions.
- Credentials configured in Jenkins for AWS, Git, and EC2 SSH access.

### Key Files

- [`Jenkinsfile`](Jenkinsfile): Defines the CI/CD pipeline.
- [`app/docker-compose.yml`](app/docker-compose.yml): Multi-container setup for local development.
- [`infrastructure/modules/ec2/`](infrastructure/modules/ec2/): Terraform code for AWS resources.
- [`infrastructure/ansible/playbook.yml`](infrastructure/ansible/playbook.yml): Ansible playbook for server configuration.

---

## How It Works

1. **Code changes** are pushed to the repository.
2. **Jenkins** triggers the pipeline, running all stages automatically.
3. **Terraform** provisions or updates AWS infrastructure.
4. **Ansible** configures the EC2 instance (Docker, AWS CLI).
5. **Docker image** is built, tested, and pushed to AWS ECR.
6. **EC2 instance** pulls and runs the new image, serving the Flask app via NGINX.

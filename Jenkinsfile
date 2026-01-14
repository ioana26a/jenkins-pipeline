pipeline {
    agent any

    environment {
        AWS_REGION = 'eu-north-1'
        ACCOUNT_ID = credentials('aws-account-id')
        ECR_REGISTRY = "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_REPO = 'ioana-dev'
        EC2_USER = 'ubuntu'
        EC2_HOST = '13.50.100.21'
    }
    stages {
        stage('Checkout') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'gitlab-tf', usernameVariable: 'GITLAB_USERNAME', passwordVariable: 'GITLAB_TOKEN')]) {
                        sh '''
                            git clone https://$GITLAB_USERNAME:$GITLAB_TOKEN@gitlab.endava.com/Vasile.Meghesan/tf-containers-pipelines.git
                        '''
                        if (params.Tag?.trim()) {
                            // Check out specific tag
                            sh """
                                cd tf-containers-pipelines
                                git checkout ${params.Tag}
                                cd jenkins-project/app
                            """
                        } else {
                            // Check out Ioana (main branch)
                            sh '''
                                cd tf-containers-pipelines
                                git checkout Ioana
                                cd jenkins-project/app
                            '''
                        }
                    }
                }
            }
        }
        stage('Test app') {
            steps {
                dir('tf-containers-pipelines/jenkins-project/app') {
                    sh '''
                        #Tells the shell to exit immediately if a command exits with a non-zero status.
                        set -e

                        # Install Python + venv if not present
                        if ! command -v python3 >/dev/null 2>&1; then
                            sudo apt-get update -y
                            sudo apt-get install -y python3 python3-pip python3-venv
                        fi

                        # Create venv if it doesn't exist
                        if [ ! -d "venv" ]; then
                            python3 -m venv venv
                        fi

                        # Activate venv
                        . venv/bin/activate

                        # Upgrade pip inside venv
                        pip install --upgrade pip

                        # Install dependencies from requirements.txt with pinned versions
                        pip install -r requirements.txt

                        # Run tests
                        pytest test_app.py

                        # Run linting checks
                        flake8 . --exclude=venv
                    '''
                }
            }
        }
        stage('Build and Tag Docker Image') {
            steps {
                dir('tf-containers-pipelines/jenkins-project/app') {
                    sh """
                        docker compose build
                        docker tag app-web:latest app-web:${params.Tag}
                        docker tag app-web:latest ${ECR_REGISTRY}/${ECR_REPO}:${params.Tag}
                    """
                }
            }
        }
        stage('Login to AWS ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-jenkins']]) {
                    sh """
                        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    """
                }
            }
        }
        stage('Push Docker Image to ECR') {
            steps {
                script {
                    sh """
                        docker push ${ECR_REGISTRY}/${ECR_REPO}:${params.Tag}
                    """
                }
            }
        }
        stage('Verify and Deploy on EC2') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    // 1. Test SSH connectivity
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} 'echo "SSH connection successful"'
                    """

                    // 2. Check Docker installation
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} 'docker --version || echo "Docker not installed"'
                    """

                    // 3. Install Docker if missing
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            if ! command -v docker >/dev/null 2>&1; then
                                sudo apt-get update
                                sudo apt-get install -y docker.io
                                sudo usermod -aG docker ${EC2_USER}
                                echo "Docker installed"
                            fi
                        '
                    """

                    // 4. Check AWS CLI installation
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} 'aws --version || echo "AWS CLI not installed"'
                    """

                    // 5. Install AWS CLI if missing
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            if ! command -v aws >/dev/null 2>&1; then
                                sudo apt-get install -y awscli
                                echo "AWS CLI installed"
                            fi
                        '
                    """

                    // 6. Authenticate to ECR
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        '
                    """

                    // 7. Pull Docker image
                    // 8. Blue-Green Deployment Script - used ports 80 and 81
                    sh """
                        cat > script_ec2.sh << 'EOF'
                        docker pull ${ECR_REGISTRY}/${ECR_REPO}:${params.Tag}

                        # 1. Find the running container and its port (80 or 81)
                        old_container=\$(docker ps --filter "name=app-web-" --format "{{.Names}}" | head -n1)
                        if [ -n "\$old_container" ]; then
                            old_port=\$(docker inspect --format='{{(index (index .NetworkSettings.Ports "80/tcp") 0).HostPort}}' "\$old_container" 2>/dev/null)
                        else
                            old_port=""
                        fi

                        # 2. Decide new port
                        if [ "\$old_port" = "80" ]; then
                            new_port=81
                        else
                            new_port=80
                        fi

                        # 3. Run new container on alternate port
                        docker run -d --name app-web-${params.Tag} -p \$new_port:80 ${ECR_REGISTRY}/${ECR_REPO}:${params.Tag}

                        # 4. Wait for health
                        for i in {1..10}; do
                            if curl -f http://localhost:\$new_port/; then
                                break
                            fi
                            sleep 3
                        done

                        # 5. Remove old container if exists
                        if [ -n "\$old_container" ]; then
                            docker stop "\$old_container"
                            docker rm "\$old_container"
                        fi
EOF
                    """
                    sh """
                        scp -o StrictHostKeyChecking=no script_ec2.sh ${EC2_USER}@${EC2_HOST}:/home/${EC2_USER}/script_ec2.sh
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} 'chmod +x /home/${EC2_USER}/script_ec2.sh && /home/${EC2_USER}/script_ec2.sh'
                    """
                }
            }
        }
        stage('Validate app on EC2') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            sleep 10
                            curl -f http://localhost:80/ || (echo "App not reachable on EC2!" && exit 1)
                            docker ps | grep app-web || (echo "Container not running!" && exit 1)
                        '
                    """
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
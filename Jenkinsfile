pipeline {
    agent any
    
    environment {
        ECR_REGISTRY = '600627353694.dkr.ecr.ap-south-1.amazonaws.com'
        ECR_REPOSITORY = 'itay/short-url'
        IMAGE_TAG = "${env.GIT_COMMIT.take(7)}"
    }
    
    stages {
        stage('Clone from GitHub') {
            steps {
                cleanWs()
                checkout scm
            }
        }
        
        stage('Unit Tests') {
            agent {
                docker {
                    image 'python:3.9'
                    reuseNode true
                }
            }
            steps {
                script {
                    sh '''
                        python -m venv venv
                        . venv/bin/activate
                        python -m pip install --upgrade pip
                        pip install -r application/requirements.txt
                        cd application
                        python -m pytest tests/ --cov=app --cov-report=xml -v
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    sh """
                        docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .
                        docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REPOSITORY}:latest
                    """
                }
            }
        }
        
        stage('Integration Test') {
            steps {
                script {
                    sh '''
                        # Create env file
                        cat > .env << EOL
MONGO_INITDB_ROOT_USERNAME=mongodb_admin
MONGO_INITDB_ROOT_PASSWORD=admin_password_123
MONGO_APP_USERNAME=url_shortener_user
MONGO_APP_PASSWORD=app_password_123
MONGO_DATABASE=urlshortener
EOL
                        
                        # Show docker-compose config for debugging
                        docker compose -f docker-compose.test.yaml config
                        
                        # Start services
                        docker compose -f docker-compose.test.yaml up -d
                        
                        # Wait a bit and check container logs
                        sleep 5
                        echo "MongoDB Logs:"
                        docker compose -f docker-compose.test.yaml logs mongodb
                        
                        # Check container status
                        echo "Container Status:"
                        docker compose -f docker-compose.test.yaml ps
                        
                        # Additional container inspection
                        echo "MongoDB Container Details:"
                        MONGO_CONTAINER_ID=$(docker compose -f docker-compose.test.yaml ps -q mongodb)
                        docker inspect $MONGO_CONTAINER_ID
                        
                        sleep 25
                        
                        # Basic health check
                        curl --fail http://localhost:80 || exit 1
                        
                        docker compose -f docker-compose.test.yaml down
                    '''
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                script {
                    withAWS(credentials: 'aws-credentials', region: 'ap-south-1') {
                        sh """
                            aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                            docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                            docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                            docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                            docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                sh '''
                    docker compose down || true
                    rm -rf venv || true
                    rm -f .env || true
                '''
                cleanWs()
            }
        }
    }
}
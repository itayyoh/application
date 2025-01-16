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
                    // Copy .env file for testing
                    sh '''
                        echo "MONGO_INITDB_ROOT_USERNAME=mongodb_admin" > .env
                        echo "MONGO_INITDB_ROOT_PASSWORD=admin_password_123" >> .env
                        echo "MONGO_APP_USERNAME=url_shortener_user" >> .env
                        echo "MONGO_APP_PASSWORD=app_password_123" >> .env
                        echo "MONGO_DATABASE=urlshortener" >> .env
                        
                        docker compose -f docker-compose.test.yaml up -d
                        sleep 30
                        
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
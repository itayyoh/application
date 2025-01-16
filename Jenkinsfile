pipeline {
    agent {
        docker {
            image 'python:3.9'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }
    
    environment {
        ECR_REGISTRY = '123456789012.dkr.ecr.region.amazonaws.com'  // Replace with your ECR registry
        ECR_REPOSITORY = 'demo-url-shortener'
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
            steps {
                script {
                    sh '''
                        python -m venv venv
                        . venv/bin/activate
                        python -m pip install --upgrade pip
                        
                        # Install requirements and test dependencies
                        pip install -r application/requirements.txt
                        pip install pytest pytest-cov
                        
                        # Create test structure
                        mkdir -p application/tests
                        
                        # Run tests from application directory
                        cd application
                        python -m pytest tests/ --cov=app --cov-report=xml -v
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} ."
                }
            }
        }
        
        stage('Integration Test') {
            steps {
                sh '''
                    docker-compose -f docker-compose.test.yaml up -d
                    sleep 30
                    curl --fail http://localhost:80 || exit 1
                    docker-compose -f docker-compose.test.yaml down
                '''
            }
        }
        
        stage('Push to ECR') {
            steps {
                script {
                    withAWS(credentials: 'aws-credentials', region: 'us-east-1') {
                        sh """
                            aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ECR_REGISTRY}
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
                    docker-compose down || true
                    rm -rf venv || true
                '''
                cleanWs()
            }
        }
    }
}
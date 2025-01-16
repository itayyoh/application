pipeline {
    agent any
    
    environment {
        ECR_REGISTRY = '600627353694.dkr.ecr.ap-south-1.amazonaws.com/itay/short-url'  // Replace with your ECR registry
        ECR_REPOSITORY = 'demo-url-shortener'
        IMAGE_TAG = "${env.GIT_COMMIT.take(7)}"
    }
    
    stages {
        stage('Clone from GitHub') {
            steps {
                // Clean workspace before cloning
                cleanWs()
                
                // Checkout from GitHub using credentials
                checkout scm
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r application/requirements.txt
                        pip install pytest pytest-cov
                        mkdir -p application/tests
                        python -m pytest application/tests/ --cov=application/app --cov-report=xml -v
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
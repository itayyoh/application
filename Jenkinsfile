pipeline {
    agent any
    
    environment {
        ECR_REGISTRY = '600627353694.dkr.ecr.ap-south-1.amazonaws.com'
        ECR_REPOSITORY = 'itay/short-url'
        IMAGE_TAG = "${env.GIT_COMMIT.take(7)}"
    }
    
    stages {
        stage('Clone') {
            steps {
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
                        cd application
                        python3 -m pytest tests/ -v
                    '''
                }
            }
        }
        
        stage('Build') {
            steps {
                script {
                    sh """
                        docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .
                        docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REPOSITORY}:latest
                    """
                }
            }
        }
        
        stage('E2E Tests') {
            steps {
                script {
                    sh '''
                        docker compose up -d
                        
                        sleep 10
                        
                        curl -X POST -H "Content-Type: application/json" \
                             -d '{"originalUrl":"https://example.com"}' \
                             http://localhost:80/shorturl/test1
                        
                        curl http://localhost:80/shorturl/test1
                        
                        curl -X PUT -H "Content-Type: application/json" \
                             -d '{"originalUrl":"https://updated-example.com"}' \
                             http://localhost:80/shorturl/test1
                        
                        curl -X DELETE http://localhost:80/shorturl/test1
                        
                        docker compose down
                    '''
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                withAWS(credentials: 'AWS-CREDENTIALS', region: 'ap-south-1') {
                    sh """
                        aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
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
pipeline {
    agent any
    
    environment {
        ECR_REGISTRY = '600627353694.dkr.ecr.ap-south-1.amazonaws.com'
        ECR_REPOSITORY = 'itay/short-url'
        IMAGE_TAG = "${env.GIT_COMMIT.take(7)}"
        FULL_IMAGE_NAME = "${ECR_REGISTRY}/${ECR_REPOSITORY}"
        AWS_DEFAULT_REGION = 'ap-south-1'
    }
    
    stages {
        stage('Clone') {
            steps {
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
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    pip install -r application/requirements.txt
                    cd application
                    python -m pytest tests/ --cov=app --cov-report=xml -v
                '''
            }
        }
        
        stage('Build') {
            steps {
                sh """
                    docker build -t ${FULL_IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${FULL_IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE_NAME}:latest
                """
            }
        }
        
        stage('E2E Tests') {
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
                        
                        # Start services
                        docker compose up -d
                        
                        # Run tests in Alpine container
                        docker run --rm \
                            --network shorturl-ci_default \
                            -v ${PWD}/e2e_tests.sh:/e2e_tests.sh \
                            alpine:3.18 \
                            sh -c "apk add --no-cache curl && sh /e2e_tests.sh"
                        
                        # Cleanup
                        docker compose down
                    '''
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                withCredentials([aws(credentialsId: 'AWS_CREDENTIALS', accessKeyVariable: 'AWS_ACCESS_KEY_ID', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh """
                        aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        docker push ${FULL_IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${FULL_IMAGE_NAME}:latest
                    """
                }
            }
        }
    }
    
    post {
        always {
            sh 'docker compose down || true'
            cleanWs()
        }
    }
}
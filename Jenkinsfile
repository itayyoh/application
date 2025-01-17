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
                    docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .
                    docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REPOSITORY}:latest
                """
            }
        }
        
        stage('E2E Tests') {
            steps {
                sh '''
                    # Debug: Print working directory and list files
                    echo "Current directory: $PWD"
                    echo "Directory contents:"
                    ls -la
                    echo "Nginx directory contents:"
                    ls -la nginx/ || echo "nginx directory not found"
                    
                    # Verify nginx config files exist
                    if [ ! -f "nginx/nginx.conf" ]; then
                        echo "Error: nginx.conf not found!"
                        exit 1
                    fi
                    
                    if [ ! -d "nginx/conf.d" ]; then
                        echo "Error: conf.d directory not found!"
                        exit 1
                    fi
                    
                    if [ ! -f "nginx/conf.d/default.conf" ]; then
                        echo "Error: default.conf not found!"
                        exit 1
                    fi

                    # Create env file
                    cat > .env << EOL
MONGO_INITDB_ROOT_USERNAME=mongodb_admin
MONGO_INITDB_ROOT_PASSWORD=admin_password_123
MONGO_APP_USERNAME=url_shortener_user
MONGO_APP_PASSWORD=app_password_123
MONGO_DATABASE=urlshortener
EOL
                    
                    # Start services and run tests
                    docker compose config  # Verify docker-compose configuration
                    docker compose up -d
                    chmod +x e2e_tests.sh
                    ./e2e_tests.sh
                    docker compose down
                '''
            }
        }
        
        stage('Push to ECR') {
            steps {
                withAWS(credentials: 'aws-credentials', region: 'ap-south-1') {
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
            sh 'docker compose down || true'
            cleanWs()
        }
    }
}
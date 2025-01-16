pipeline {
    agent any
    
    environment {
        ECR_REGISTRY = credentials('ecr-registry')
        ECR_REPOSITORY = 'demo-url-shortener'
        IMAGE_TAG = "${env.GIT_COMMIT.take(7)}"
    }
    
    stages {
        stage('Clone from GitHub') {
            steps {
                // Clean workspace before cloning
                cleanWs()
                
                // Checkout from GitHub using credentials
                git branch: 'main',
                    credentialsId: 'github-credentials',
                    url: 'https://github.com/YOUR_USERNAME/url-shortener.git' // change username
            }
        }
        
        stage('Unit Tests') {
            steps {
                script {
                    // Create and activate virtual environment
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        
                        # Install dependencies and pytest
                        pip install -r application/requirements.txt
                        pip install pytest pytest-cov
                        
                        # Create tests directory if it doesn't exist
                        mkdir -p application/tests
                        
                        # Run tests with coverage
                        cd application
                        python -m pytest tests/ --cov=app --cov-report=xml -v
                    '''
                }
            }
            post {
                success {
                    // Archive test results and coverage report
                    junit allowEmptyResults: true, testResults: '**/test-results/*.xml'
                    publishCoverage adapters: [coberturaAdapter('**/coverage.xml')]
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${ECR_REPOSITORY}:${IMAGE_TAG}", "-f Dockerfile .")
                }
            }
        }
        
        stage('Integration Test') {
            steps {
                sh '''
                    docker-compose -f docker-compose.test.yaml up -d
                    sleep 30  # Wait for services to be healthy
                    
                    # Basic health check
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
            // Cleanup
            sh '''
                docker-compose down || true
                docker rmi ${ECR_REPOSITORY}:${IMAGE_TAG} || true
            '''
            cleanWs()
        }
    }
}
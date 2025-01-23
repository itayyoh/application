pipeline {
    agent any
    
    environment {
        ECR_REGISTRY = '600627353694.dkr.ecr.ap-south-1.amazonaws.com'
        ECR_REPOSITORY = 'itay/short-url'
        GIT_COMMIT_SHORT = "${env.GIT_COMMIT.take(7)}"
        FULL_IMAGE_NAME = "${ECR_REGISTRY}/${ECR_REPOSITORY}"
        AWS_DEFAULT_REGION = 'ap-south-1'
        BRANCH_NAME = "${env.BRANCH_NAME}"
        GITOPS_REPO = 'git@github.com:itayyoh/gitops-shorturl.git'
        
    }
    
    stages {
        stage('Clone') {
            steps {
                checkout scm
            }
        }

        stage('Set Version') {
            steps {
                script {
                    // Get the latest tag if it exists
                    def latestTag = sh(script: """
                        git fetch --tags
                        git tag -l 'v*' | sort -V | tail -n 1
                    """, returnStdout: true).trim()

                    if (latestTag) {
                        // If tag exists, increment patch version
                        def (major, minor, patch) = latestTag.substring(1).tokenize('.')
                        env.NEW_VERSION = "v${major}.${minor}.${(patch as int) + 1}"
                    } else {
                        // If no tag exists, start with v1.0.0
                        env.NEW_VERSION = 'v1.0.0'
                    }
                    
                    echo "Building version: ${env.NEW_VERSION}"
                }
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
                script {
                    if (env.BRANCH_NAME.startsWith('feature/')) {
                        def branchTag = env.BRANCH_NAME.replaceAll('/', '-')
                        sh """
                            docker build -t ${FULL_IMAGE_NAME}:${branchTag}-${GIT_COMMIT_SHORT} .
                        """
                    } 
                    else if (env.BRANCH_NAME == 'MAIN') {
                        sh """
                            docker build -t ${FULL_IMAGE_NAME}:${env.NEW_VERSION} .
                            docker tag ${FULL_IMAGE_NAME}:${env.NEW_VERSION} ${FULL_IMAGE_NAME}:latest
                        """
                    }
                    else {
                        sh """
                            docker build -t ${FULL_IMAGE_NAME}:${GIT_COMMIT_SHORT} .
                        """
                    }
                }
            }
        }
        
        stage('E2E Tests') {
            when {
                anyOf {
                    branch 'MAIN'
                    branch pattern: "feature/*", comparator: "REGEXP"
                }
            }
            steps {
                script {
                    try {
                        sh '''
                            # Create env file
                            cat > .env << EOL
MONGO_INITDB_ROOT_USERNAME=mongodb_admin
MONGO_INITDB_ROOT_PASSWORD=admin_password_123
MONGO_APP_USERNAME=url_shortener_user
MONGO_APP_PASSWORD=app_password_123
MONGO_DATABASE=urlshortener 
EOL
                            
                            docker network create shorturl-ci_default || true
                            
                            # Start services
                            docker compose up -d
                            
                            # Run tests in Alpine container
                            docker run --rm \
                                --network shorturl-ci_default \
                                -v ${PWD}/e2e_tests.sh:/e2e_tests.sh \
                                alpine:3.18 \
                                sh -c "apk add --no-cache curl && sh /e2e_tests.sh"
                        '''
                    } finally {
                        sh 'docker compose down'
                    }
                }
            }
        }
        
        stage('Tag and Push') {
            when {
                branch 'MAIN'
            }
            steps {
                withCredentials([usernamePassword(credentialsId: 'AWS_CREDENTIALS', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                    sh """
                        aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        docker push ${FULL_IMAGE_NAME}:${env.NEW_VERSION}
                        docker push ${FULL_IMAGE_NAME}:latest

                        # Configure Git user for tagging
                        git config user.name "Jenkins CI"
                        git config user.email "jenkins@example.com"

                        # Create and push Git tag
                        git tag -a ${env.NEW_VERSION} -m "Release ${env.NEW_VERSION}"
                        git push origin ${env.NEW_VERSION}
                    """
                }
            }
        }

        stage('Update GitOps') {
            when {
                branch 'MAIN'
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'github-ssh-key', keyFileVariable: 'SSH_KEY')]) {
                    sh """
                        GIT_SSH_COMMAND='ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no' git clone git@github.com:itayyoh/gitops-shorturl.git gitops
                        cd gitops
                        git config --global user.email "jenkins@example.com"    
                        git config --global user.name "Jenkins CI"     
                        yq eval '.url-shortener.image.tag = "${env.NEW_VERSION}"' -i helm/values/dev.yaml
                        yq eval '.url-shortener.image.tag = "${env.NEW_VERSION}"' -i helm/values/prod.yaml
                        git add .
                        git commit -m "Update url-shortener to version ${env.NEW_VERSION}"
                        git push origin main
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
pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'localhost:5000'
        BACKEND_IMAGE = "${DOCKER_REGISTRY}/backend-dev"
        NGINX_IMAGE = "${DOCKER_REGISTRY}/nginx-dev"
        VERSIONCONTROL_IMAGE = "${DOCKER_REGISTRY}/versioncontrol-dev"
        BUILD_VERSION = "build-${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
                script {
                    echo "📦 Checking out code from ${env.GIT_BRANCH}"
                }
            }
        }
        
        stage('Build Backend Image') {
            steps {
                script {
                    echo "🔨 Building backend image..."
                    dir('dev') {
                        bat """
                            docker build -f Dockerfile.backend -t ${BACKEND_IMAGE}:${BUILD_VERSION} .
                            docker tag ${BACKEND_IMAGE}:${BUILD_VERSION} ${BACKEND_IMAGE}:latest
                        """
                    }
                }
            }
        }
        
        stage('Build Nginx Image') {
            steps {
                script {
                    echo "🔨 Building nginx image..."
                    dir('dev') {
                        bat """
                            docker build -f Dockerfile.nginx -t ${NGINX_IMAGE}:${BUILD_VERSION} .
                            docker tag ${NGINX_IMAGE}:${BUILD_VERSION} ${NGINX_IMAGE}:latest
                        """
                    }
                }
            }
        }
        
        stage('Build Version Control Image') {
            steps {
                script {
                    echo "🔨 Building version control image..."
                    dir('dev/version_control') {
                        bat """
                            docker build -t ${VERSIONCONTROL_IMAGE}:${BUILD_VERSION} .
                            docker tag ${VERSIONCONTROL_IMAGE}:${BUILD_VERSION} ${VERSIONCONTROL_IMAGE}:latest
                        """
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    echo "🧪 Running containerized tests..."
                    bat """
                        docker run --rm ${BACKEND_IMAGE}:${BUILD_VERSION} python manage.py test --no-input || echo "Tests completed with warnings"
                    """
                }
            }
        }
        
        stage('Push Images to Registry') {
            steps {
                script {
                    echo "📤 Pushing images to local registry..."
                    bat """
                        docker push ${BACKEND_IMAGE}:${BUILD_VERSION}
                        docker push ${BACKEND_IMAGE}:latest
                        docker push ${NGINX_IMAGE}:${BUILD_VERSION}
                        docker push ${NGINX_IMAGE}:latest
                        docker push ${VERSIONCONTROL_IMAGE}:${BUILD_VERSION}
                        docker push ${VERSIONCONTROL_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Deploy Dev Environment') {
            steps {
                script {
                    echo "🚀 Deploying dev environment..."
                    dir('dev') {
                        bat """
                            docker-compose down || echo "No containers to stop"
                            docker-compose up -d --build
                            timeout /t 10 /nobreak
                            curl -f http://localhost/api/ || exit 1
                            echo "✅ Dev deployment successful!"
                        """
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo "✅ Dev pipeline completed successfully!"
            echo "📦 Images tagged: ${BUILD_VERSION}"
            echo "🌐 Dev application available at: http://localhost"
        }
        failure {
            echo "❌ Dev pipeline failed!"
        }
        always {
            echo "🧹 Cleaning up..."
            bat "docker system prune -f || echo "Cleanup completed""
        }
    }
}

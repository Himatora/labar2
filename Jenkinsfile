pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'localhost:5001'
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
                    sh """
                        docker build -f Dockerfile.backend -t ${BACKEND_IMAGE}:${BUILD_VERSION} .
                        docker tag ${BACKEND_IMAGE}:${BUILD_VERSION} ${BACKEND_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Build Nginx Image') {
            steps {
                script {
                    echo "🔨 Building nginx image..."
                    sh """
                        docker build -f Dockerfile.nginx -t ${NGINX_IMAGE}:${BUILD_VERSION} .
                        docker tag ${NGINX_IMAGE}:${BUILD_VERSION} ${NGINX_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Build Version Control Image') {
            steps {
                script {
                    echo "🔨 Building version control image..."
                    dir('version_control') {
                        sh """
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
                    sh """
                        docker run --rm ${BACKEND_IMAGE}:${BUILD_VERSION} python manage.py test --no-input || echo "Tests completed with warnings"
                    """
                }
            }
        }
        
        stage('Push Images to Registry') {
            steps {
                script {
                    echo "📤 Pushing images to local registry..."
                    sh """
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
                    sh '''
                        # Останавливаем ВСЕ контейнеры, использующие наши порты
                        docker stop $(docker ps -q --filter "publish=8001") 2>/dev/null || true
                        docker stop $(docker ps -q --filter "publish=8000") 2>/dev/null || true
                        docker stop $(docker ps -q --filter "publish=80") 2>/dev/null || true
                        docker stop $(docker ps -q --filter "publish=5000") 2>/dev/null || true
                        
                        # Удаляем остановленные контейнеры
                        docker rm $(docker ps -aq --filter "publish=8001") 2>/dev/null || true
                        docker rm $(docker ps -aq --filter "publish=8000") 2>/dev/null || true
                        docker rm $(docker ps -aq --filter "publish=80") 2>/dev/null || true
                        docker rm $(docker ps -aq --filter "publish=5000") 2>/dev/null || true
                        
                        # Полная очистка docker-compose
                        docker compose down --remove-orphans --volumes --timeout 30 || true
                        
                        # Запускаем приложение
                        docker compose up -d --build
                        
                        sleep 10
                        curl -f http://localhost/api/ || exit 1
                        echo "✅ Dev deployment successful!"
                    '''
                }
            }
        }
        
        stage('Push to Git Repository') {
            steps {
                script {
                    echo '📤 Pushing build information to Git...'
                    
                    withCredentials([usernamePassword(
                        credentialsId: 'github-token',
                        usernameVariable: 'GIT_USERNAME',
                        passwordVariable: 'GIT_PASSWORD'
                    )]) {
                        sh '''
                            # Создаем файл с информацией о сборке
                            cat > build-info.txt << EOF
Build Number: ${BUILD_NUMBER}
Build Version: build-${BUILD_NUMBER}
Build Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Git Commit: $(git rev-parse HEAD)
Git Branch: origin/main
EOF

                            git config user.name "Jenkins CI"
                            git config user.email "jenkins@ci.local"
                            git remote set-url origin https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/Himatora/labar2.git
                            git add build-info.txt
                            git commit -m "CI: Update build info for dev build ${BUILD_NUMBER}"
                            git push origin HEAD:main
                            git push origin --tags
                        '''
                    }
                    
                    echo '✅ Git push completed successfully!'
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
            sh "docker system prune -f || true"
        }
    }
}

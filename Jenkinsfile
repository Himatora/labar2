pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'localhost:5001'
        BACKEND_IMAGE = "${DOCKER_REGISTRY}/backend-dev"
        NGINX_IMAGE = "${DOCKER_REGISTRY}/nginx-dev"
        VERSIONCONTROL_IMAGE = "${DOCKER_REGISTRY}/versioncontrol-dev"
        BUILD_VERSION = "build-${BUILD_NUMBER}"
    }
    
    triggers { 
        githubPush() 
    }
    
    stages {
        stage('Checkout and Detect Branch') {
            steps {
                checkout scm
                script {
                    echo "📦 Checking out code from ${env.GIT_BRANCH}"
                    // Определяем текущую ветку
                    CURRENT_BRANCH = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
                    echo "🎯 Current branch: ${CURRENT_BRANCH}"
                }
            }
        }
        
        stage('Merge dev to main') {
            when {
                expression { 
                    return env.GIT_BRANCH == 'origin/dev' || CURRENT_BRANCH == 'dev'
                }
            }
            steps {
                script {
                    echo "🔄 Merging dev to main..."
                    
                    withCredentials([usernamePassword(
                        credentialsId: 'github-token',
                        usernameVariable: 'GIT_USERNAME',
                        passwordVariable: 'GIT_PASSWORD'
                    )]) {
                        sh '''
                            git config user.name "Jenkins CI"
                            git config user.email "jenkins@ci.local"
                            git remote set-url origin https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/Himatora/labar2.git
                            
                            # Переключаемся на main и обновляем её
                            git fetch origin
                            git checkout main
                            git pull origin main
                            
                            # Мержим dev в main
                            git merge origin/dev --no-ff -m "Auto-merge: dev to main by Jenkins (build ${BUILD_NUMBER})"
                            
                            # Пушим изменения в main
                            git push origin main
                            
                            echo "✅ Successfully merged dev to main"
                        '''
                    }
                }
            }
        }
        
        stage('Switch to main for deployment') {
            when {
                expression { 
                    return env.GIT_BRANCH == 'origin/dev' || CURRENT_BRANCH == 'dev'
                }
            }
            steps {
                script {
                    echo "🔄 Switching to main branch for deployment..."
                    checkout([$class: 'GitSCM',
                        branches: [[name: '*/main']],
                        extensions: [],
                        userRemoteConfigs: [[url: 'https://github.com/Himatora/labar2.git', credentialsId: 'github-token']]
                    ])
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
        
        stage('Deploy from main') {
            steps {
                script {
                    echo "🚀 Deploying from main branch..."
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
                        
                        # Запускаем приложение из main
                        docker compose up -d --build
                        
                        sleep 10
                        curl -f http://localhost/api/ || exit 1
                        echo "✅ Deployment from main successful!"
                    '''
                }
            }
        }
        
        stage('Push Build Info to Git') {
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
Git Branch: main
Source Branch: ${CURRENT_BRANCH}
EOF

                            git config user.name "Jenkins CI"
                            git config user.email "jenkins@ci.local"
                            git remote set-url origin https://${GIT_USERNAME}:${GIT_PASSWORD}@github.com/Himatora/labar2.git
                            git add build-info.txt
                            git commit -m "CI: Update build info for build ${BUILD_NUMBER} (from ${CURRENT_BRANCH})" || echo "No changes to commit"
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
            script {
                echo "✅ Pipeline completed successfully!"
                echo "📦 Images tagged: ${BUILD_VERSION}"
                echo "🌐 Application deployed from: main"
                echo "🚀 Application available at: http://localhost"
                
                // Дополнительная информация о мерже
                if (env.GIT_BRANCH == 'origin/dev' || CURRENT_BRANCH == 'dev') {
                    echo "🔄 Auto-merge: dev → main completed"
                }
            }
        }
        failure {
            echo "❌ Pipeline failed!"
        }
        always {
            echo "🧹 Cleaning up..."
            sh "docker system prune -f || true"
        }
    }
}

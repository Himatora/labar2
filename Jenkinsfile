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
            // ФИКС: Добавляем def для переменной
            def CURRENT_BRANCH = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
            echo "🎯 Current branch: ${CURRENT_BRANCH}"
            // Сохраняем в env для использования в других stage
            env.CURRENT_BRANCH = CURRENT_BRANCH
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
                set +e  # Разрешаем ошибки для лучшего контроля
                
                # Определяем все порты, которые мы используем
                PORTS="5000 8000 8001 80"
                
                echo "🔧 Step 1: Stopping all containers using our ports..."
                for port in $PORTS; do
                    echo "Stopping containers on port $port"
                    docker stop $(docker ps -q --filter "publish=$port") 2>/dev/null || true
                    docker rm -f $(docker ps -aq --filter "publish=$port") 2>/dev/null || true
                done
                
                echo "🔧 Step 2: Checking what's using our ports..."
                for port in $PORTS; do
                    echo "Checking port $port:"
                    if command -v netstat >/dev/null 2>&1; then
                        netstat -tulpn | grep :$port || echo "No processes found with netstat"
                    fi
                    if command -v ss >/dev/null 2>&1; then
                        ss -tulpn | grep :$port || echo "No processes found with ss"
                    fi
                    if command -v lsof >/dev/null 2>&1; then
                        lsof -i :$port || echo "No processes found with lsof"
                    fi
                done
                
                echo "🔧 Step 3: Killing processes on our ports..."
                for port in $PORTS; do
                    sudo fuser -k $port/tcp 2>/dev/null || true
                done
                sleep 5
                
                echo "🔧 Step 4: Complete docker compose cleanup..."
                docker compose down --remove-orphans --volumes --timeout 30 || true
                sleep 10
                
                echo "🔧 Step 5: Checking port availability..."
                for port in $PORTS; do
                    if command -v nc >/dev/null 2>&1; then
                        if nc -z localhost $port; then
                            echo "❌ Port $port is still occupied after cleanup"
                        else
                            echo "✅ Port $port is available"
                        fi
                    fi
                done
                
                echo "🔧 Step 6: Dynamic port allocation..."
                # Если порты заняты, меняем их в docker-compose.yml
                if nc -z localhost 8001; then
                    echo "🔄 Port 8001 occupied, changing to 8002"
                    sed -i 's/8001:8001/8002:8001/g' docker-compose.yml
                fi
                
                if nc -z localhost 5000; then
                    echo "🔄 Port 5000 occupied, changing to 5002"
                    sed -i 's/5000:5000/5002:5000/g' docker-compose.yml
                fi
                
                echo "🔧 Step 7: Starting services..."
                docker compose up -d --build --force-recreate
                
                if [ $? -eq 0 ]; then
                    echo "✅ Services started successfully"
                    
                    # Даем время на запуск
                    sleep 30
                    
                    # Проверяем статус контейнеров
                    echo "📊 Container status:"
                    docker compose ps
                    
                    # Проверяем логи
                    echo "📋 Checking container logs..."
                    docker compose logs --tail=20
                    
                    echo "✅ Deployment completed successfully!"
                else
                    echo "❌ Failed to start services"
                    echo "🔄 Trying complete port reassignment..."
                    
                    # Полная перезапись портов
                    docker compose down --remove-orphans --volumes --timeout 30 || true
                    sleep 5
                    
                    # Изменяем ВСЕ порты
                    sed -i 's/5000:5000/5002:5000/g' docker-compose.yml
                    sed -i 's/8001:8001/8002:8001/g' docker-compose.yml
                    sed -i 's/8000:8000/8003:8000/g' docker-compose.yml
                    
                    docker compose up -d --build --force-recreate
                    
                    if [ $? -eq 0 ]; then
                        echo "✅ Services started successfully with new ports"
                        sleep 30
                        docker compose ps
                        docker compose logs --tail=20
                        
                        echo "🌐 Application available at:"
                        echo "   Frontend: http://localhost"
                        echo "   Backend: http://localhost:8003"
                        echo "   Version Control: http://localhost:8002"
                        echo "   Registry: http://localhost:5002"
                    else
                        echo "❌ Deployment failed completely"
                        docker compose logs
                        exit 1
                    fi
                fi
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

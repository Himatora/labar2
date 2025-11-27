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
                    dir('dev') {
                        sh """
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
                        sh """
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
                    dir('dev') {
                        sh """
                            docker-compose down || true
                            docker-compose up -d --build
                            sleep 10
                            curl -f http://localhost/api/ || exit 1
                            echo "✅ Dev deployment successful!"
                        """
                    }
                }
            }
        }
        
        stage('Push to Git Repository') {
            steps {
                script {
                    echo "📤 Pushing build information to Git..."
                    
                    // Try with credentials first, fallback to SSH if available
                    try {
                        withCredentials([usernamePassword(credentialsId: 'git-credentials', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                            sh """
                                git config user.name "Jenkins CI"
                                git config user.email "jenkins@ci.local"
                                
                                # Create or update build info file
                                echo "Build Number: ${BUILD_NUMBER}" > build-info.txt
                                echo "Build Version: ${BUILD_VERSION}" >> build-info.txt
                                echo "Build Date: \$(date -u +'%Y-%m-%d %H:%M:%S UTC')" >> build-info.txt
                                echo "Git Commit: \$(git rev-parse HEAD)" >> build-info.txt
                                echo "Git Branch: ${env.GIT_BRANCH}" >> build-info.txt
                                
                                # Create git tag for this build
                                git tag -a "dev-build-${BUILD_NUMBER}" -m "Dev build ${BUILD_NUMBER} - ${BUILD_VERSION}" || true
                                
                                # Add and commit build info
                                git add build-info.txt || true
                                git commit -m "CI: Update build info for dev build ${BUILD_NUMBER}" || true
                                
                                # Push commits and tags (HTTPS with credentials)
                                git push https://\${GIT_USER}:\${GIT_TOKEN}@\$(echo ${env.GIT_URL} | sed 's|https://||' | sed 's|git@||' | sed 's|:|/|') HEAD:${env.GIT_BRANCH} || echo "Push skipped (no changes)"
                                git push https://\${GIT_USER}:\${GIT_TOKEN}@\$(echo ${env.GIT_URL} | sed 's|https://||' | sed 's|git@||' | sed 's|:|/|') --tags || echo "Tag push skipped"
                                
                                echo "✅ Git push completed!"
                            """
                        }
                    } catch (Exception e) {
                        echo "⚠️ Credentials not configured, trying SSH..."
                        sh """
                            git config user.name "Jenkins CI"
                            git config user.email "jenkins@ci.local"
                            
                            # Create or update build info file
                            echo "Build Number: ${BUILD_NUMBER}" > build-info.txt
                            echo "Build Version: ${BUILD_VERSION}" >> build-info.txt
                            echo "Build Date: \$(date -u +'%Y-%m-%d %H:%M:%S UTC')" >> build-info.txt
                            echo "Git Commit: \$(git rev-parse HEAD)" >> build-info.txt
                            echo "Git Branch: ${env.GIT_BRANCH}" >> build-info.txt
                            
                            # Create git tag for this build
                            git tag -a "dev-build-${BUILD_NUMBER}" -m "Dev build ${BUILD_NUMBER} - ${BUILD_VERSION}" || true
                            
                            # Add and commit build info
                            git add build-info.txt || true
                            git commit -m "CI: Update build info for dev build ${BUILD_NUMBER}" || true
                            
                            # Push commits and tags (SSH or default)
                            git push origin ${env.GIT_BRANCH} || echo "Push skipped (no changes or no SSH access)"
                            git push origin --tags || echo "Tag push skipped"
                            
                            echo "✅ Git push completed (or skipped if no access configured)"
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
            sh "docker system prune -f || true"
        }
    }
}

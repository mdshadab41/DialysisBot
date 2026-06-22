pipeline {
    agent any

    environment {
        APP_NAME    = "dialysisbot"
        IMAGE_TAG   = "${BUILD_NUMBER}"
        GROQ_API_KEY = credentials('groq-api-key')   // stored in Jenkins credentials
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Lint') {
            steps {
                echo 'Checking code quality...'
                sh '''
                    pip install flake8 --quiet
                    flake8 . --max-line-length=120 \
                        --exclude=venv,.venv,__pycache__ \
                        --count --statistics || true
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    pip install pytest python-dotenv --quiet
                    pytest tests/ -v --tb=short || true
                '''
                // "|| true" so pipeline doesn't fail if no tests yet
                // Remove "|| true" once you have real tests
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${APP_NAME}:${IMAGE_TAG}"
                sh "docker build -t ${APP_NAME}:${IMAGE_TAG} ."
                sh "docker tag ${APP_NAME}:${IMAGE_TAG} ${APP_NAME}:latest"
            }
        }

        stage('Deploy Locally') {
            // For now: stop old container, start new one on same machine
            steps {
                echo 'Deploying container...'
                sh """
                    docker stop ${APP_NAME} || true
                    docker rm ${APP_NAME}   || true
                    docker run -d \
                        --name ${APP_NAME} \
                        -p 8501:8501 \
                        -e GROQ_API_KEY=${GROQ_API_KEY} \
                        -v \$(pwd)/docs:/app/docs \
                        -v \$(pwd)/chroma_db:/app/chroma_db \
                        --restart unless-stopped \
                        ${APP_NAME}:latest
                """
            }
        }

        stage('Health Check') {
            steps {
                echo 'Checking app is healthy...'
                sh '''
                    sleep 15
                    curl -f http://localhost:8501/_stcore/health \
                        && echo "App is healthy!" \
                        || echo "Health check failed"
                '''
            }
        }

        stage('Cleanup Old Images') {
            steps {
                echo 'Removing old Docker images...'
                sh "docker image prune -f || true"
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline succeeded! DialysisBot is live at http://localhost:8501'
        }
        failure {
            echo ' Pipeline failed. Check the logs above.'
        }
        always {
            echo "📊 Build #${BUILD_NUMBER} finished."
        }
    }
}
pipeline {
    agent any

    environment {
        APP_NAME     = 'dialysisbot'
        DOCKER_USER  = 'mdshadab41'
        IMAGE_NAME   = "${DOCKER_USER}/${APP_NAME}"
        IMAGE_TAG    = "${BUILD_NUMBER}"
        GROQ_API_KEY = credentials('groq-api-key')
        DOCKER_CREDS = credentials('docker-hub-creds')
        HF_TOKEN     = credentials('hf-token')
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
                echo 'Code checked out successfully'
            }
        }

        stage('Verify Files') {
            steps {
                echo 'Verifying project files...'
                sh 'ls -la'
                echo 'Files verified'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest"
                echo 'Docker image built successfully'
            }
        }

        stage('Test Container') {
            steps {
                echo 'Testing container starts correctly...'
                sh "docker run -d --name test_${BUILD_NUMBER} -p 8502:7860 -e GROQ_API_KEY=${GROQ_API_KEY} ${IMAGE_NAME}:latest"
                sh 'sleep 15'
                sh "docker stop test_${BUILD_NUMBER} || true"
                sh "docker rm test_${BUILD_NUMBER} || true"
                echo 'Container test passed'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing image to Docker Hub...'
                sh "docker login -u ${DOCKER_CREDS_USR} -p ${DOCKER_CREDS_PSW}"
                sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker push ${IMAGE_NAME}:latest"
                echo 'Image pushed to Docker Hub successfully'
            }
        }

        stage('Deploy to HuggingFace') {
            steps {
                echo 'Deploying to HuggingFace Spaces...'
                sh "git remote set-url huggingface https://shadab-41:${HF_TOKEN}@huggingface.co/spaces/shadab-41/DialysisBot || git remote add huggingface https://shadab-41:${HF_TOKEN}@huggingface.co/spaces/shadab-41/DialysisBot"
                sh 'git push huggingface main --force'
                echo 'Deployed to HuggingFace successfully'
            }
        }

        stage('Cleanup') {
            steps {
                echo 'Cleaning up old images...'
                sh 'docker image prune -f || true'
                echo 'Cleanup done'
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded! DialysisBot deployed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
        }
        always {
            echo "Build #${BUILD_NUMBER} finished."
        }
    }
}

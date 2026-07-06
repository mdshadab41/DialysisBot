pipeline {
    agent any

    environment {
        APP_NAME     = 'dialysisbot'
        AWS_REGION   = 'ap-south-1'
        ECR_REGISTRY = '806528484602.dkr.ecr.ap-south-1.amazonaws.com'
        ECR_REPO     = "${ECR_REGISTRY}/${APP_NAME}"
        IMAGE_TAG    = "${BUILD_NUMBER}"
        GROQ_API_KEY = credentials('groq-api-key')
        HF_TOKEN     = credentials('hf-token')
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-key')
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
                echo '🔍 Verifying project files...'
                sh 'ls -la'
                echo 'Files verified'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${ECR_REPO}:${IMAGE_TAG}"
                sh "docker build -t ${ECR_REPO}:${IMAGE_TAG} ."
                sh "docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_REPO}:latest"
                echo 'Docker image built successfully'
            }
        }

        stage('Test Container') {
            steps {
                echo 'Testing container...'
                sh "docker run -d --name test_${BUILD_NUMBER} -p 8502:7860 -e GROQ_API_KEY=${GROQ_API_KEY} ${ECR_REPO}:latest"
                sh 'sleep 15'
                sh "docker stop test_${BUILD_NUMBER} || true"
                sh "docker rm test_${BUILD_NUMBER} || true"
                echo '✅ Container test passed'
            }
        }

        stage('Push to AWS ECR') {
            steps {
                echo 'Pushing image to AWS ECR...'
                sh """
                    aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS \
                    --password-stdin ${ECR_REGISTRY}
                """
                sh "docker push ${ECR_REPO}:${IMAGE_TAG}"
                sh "docker push ${ECR_REPO}:latest"
                echo 'Image pushed to ECR successfully'
            }
        }

        stage('Deploy to HuggingFace') {
            steps {
                echo 'Deploying to HuggingFace Spaces...'
                sh '''
                    git config --global user.email "shadab@dialysisbot.com"
                    git config --global user.name "Shadab Rayeen"
                    git remote remove huggingface || true
                    git remote add huggingface https://shadab-41:$HF_TOKEN@huggingface.co/spaces/shadab-41/DialysisBot
                    git push huggingface HEAD:main --force
                '''
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

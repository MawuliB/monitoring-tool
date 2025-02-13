def loginToDockerHub() {
    withCredentials([usernamePassword(credentialsId: 'docker-hub-cred', usernameVariable: 'DOCKER_HUB_USERNAME', passwordVariable: 'DOCKER_HUB_PASSWORD')]) {
        sh "echo ${DOCKER_HUB_PASSWORD} | docker login -u ${DOCKER_HUB_USERNAME} --password-stdin"
    }
}

def buildAndPushToDockerHub() {
    sh '''
        docker compose build
        docker compose push
    '''
}

def cleanup() {
    sh 'docker volume prune -f && docker system prune -f'
}

pipeline {
    agent {
        label 'agent1'
    }

    environment {
        INSTANCE_USER = 'ubuntu'
        INSTANCE_IP = '18.201.187.71'
    }

    stages {
        stage('Push to Docker Hub') {
            steps {
                script {
                    loginToDockerHub()
                    buildAndPushToDockerHub()
                    cleanup()
                }
            }
        }

        stage('Deployment') {
            steps {
                sshagent(['monitoring-key']) {
                    sh '''
                        scp -o StrictHostKeyChecking=no -r ./docker-compose.yml ${INSTANCE_USER}@${INSTANCE_IP}:/home/${INSTANCE_USER}/
                        ssh -o StrictHostKeyChecking=no ${INSTANCE_USER}@${INSTANCE_IP} "docker compose pull && docker compose up -d"
                    '''
                }
            }
        }
    }
    post {
        always {
            cleanup()
            cleanWs()
        }
    }
}
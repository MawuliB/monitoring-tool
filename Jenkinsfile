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
                        scp -o StrictHostKeyChecking=no -r ./docker-compose.yml mawuli@68.154.68.179:/home/mawuli
                        ssh -o StrictHostKeyChecking=no mawuli@68.154.68.179 "docker compose pull && docker compose up -d"
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
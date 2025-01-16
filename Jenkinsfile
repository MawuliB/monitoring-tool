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
    }
}
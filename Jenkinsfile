pipeline {
    agent any

    environment {
        // Rancher info
        RANCHER_URL = 'http://10.48.10.140'
        RANCHER_ACCESS_KEY = credentials('Access-Key')
        RANCHER_SECRET_KEY = credentials('Secret-Key')

        // Jenkins info
        JENKINS_URL = 'http://10.48.10.145:8080'
        JENKINS_USER = 'taylorw8'
        JENKINS_TOKEN = credentials('jenkins-api-token')
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build('rancher-jenkins-sync')
                }
            }
        }

        stage('Run Rancher Sync') {
            steps {
                script {
                    docker.image('rancher-jenkins-sync').inside(
                        "--env RANCHER_URL=${env.RANCHER_URL} " +
                        "--env RANCHER_ACCESS_KEY=${env.RANCHER_ACCESS_KEY} " +
                        "--env RANCHER_SECRET_KEY=${env.RANCHER_SECRET_KEY} " +
                        "--env JENKINS_URL=${env.JENKINS_URL} " +
                        "--env JENKINS_USER=${env.JENKINS_USER} " +
                        "--env JENKINS_TOKEN=${env.JENKINS_TOKEN}"
                    ) {
                        sh 'python rancher_to_jenkins.py'
                    }
                }
            }
        }
    }
}

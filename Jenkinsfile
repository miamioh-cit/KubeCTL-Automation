pipeline {
    agent any

    environment {
        RANCHER_URL = 'http://10.48.10.140'
        JENKINS_URL = 'http://10.48.10.145:8080'
        JENKINS_USER = 'taylorw8'
        RANCHER_TOKEN = credentials('rancher-api-token')
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

        stage('Run Sync Script') {
            steps {
                script {
                    docker.image('rancher-jenkins-sync').inside(
                        "--env RANCHER_URL=${env.RANCHER_URL} " +
                        "--env RANCHER_TOKEN=${env.RANCHER_TOKEN} " +
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

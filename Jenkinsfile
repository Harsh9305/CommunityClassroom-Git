pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://github.com/Harsh9305/CommunityClassroom-Git.git'
            }
        }
        
        stage('Calculate Average Grade') {
            steps {
                script {
                    // Run the Python script
                    sh 'python3 p1.py'
                }
            }
        }
        
        stage('Archive the Result') {
            steps {
                archiveArtifacts artifacts: 'average_grade.txt'
            }
        }
    }
}

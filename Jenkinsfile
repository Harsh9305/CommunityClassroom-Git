pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                git 'https://your-git-repository-url.git'
            }
        }
        
        stage('Calculate Average Grade') {
            steps {
                script {
                    // Run the Python script
                    sh 'python3 calculate_average.py'
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

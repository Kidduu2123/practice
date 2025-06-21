pipeline {
    agent any
    stages {
        stage('Check and Clean') {
            steps {
                script {
                    if (fileExists('pom.xml')) {
                        sh 'mvn clean'
                    } else {
                        echo "pom.xml not found"
                    }
                }
            }
        }
    }
}

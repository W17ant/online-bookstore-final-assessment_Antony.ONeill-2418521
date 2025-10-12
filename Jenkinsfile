pipeline {
    agent any

    environment {
        // Python virtual environment path
        VENV_PATH = "${WORKSPACE}/venv"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                sh '''
                    python3 -m venv ${VENV_PATH}
                    . ${VENV_PATH}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running test suite with coverage...'
                sh '''
                    . ${VENV_PATH}/bin/activate
                    mkdir -p reports
                    pytest tests/ -v \
                        --junitxml=reports/junit.xml \
                        --cov=. \
                        --cov-report=xml:reports/coverage.xml \
                        --cov-report=html:reports/htmlcov \
                        --cov-report=term
                '''
            }
        }

        stage('Generate Allure Report') {
            steps {
                echo 'Generating Allure test report...'
                sh '''
                    . ${VENV_PATH}/bin/activate
                    mkdir -p allure-results
                    pytest tests/ -v \
                        --alluredir=allure-results
                '''
            }
        }
    }

    post {
        always {
            echo 'Publishing test results and reports...'

            // Publish JUnit test results
            junit 'reports/junit.xml'

            // Publish Cobertura coverage report
            cobertura coberturaReportFile: 'reports/coverage.xml',
                      autoUpdateHealth: false,
                      autoUpdateStability: false,
                      failUnhealthy: false,
                      failUnstable: false,
                      maxNumberOfBuilds: 10,
                      onlyStable: false,
                      sourceEncoding: 'ASCII',
                      zoomCoverageChart: false

            // Publish HTML coverage report
            publishHTML(target: [
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports/htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report',
                reportTitles: 'Test Coverage Report'
            ])

            // Publish Allure report
            allure includeProperties: false,
                   jdk: '',
                   results: [[path: 'allure-results']]
        }

        success {
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Please check the logs.'
        }

        cleanup {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
    }
}

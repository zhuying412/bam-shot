pipeline {
  agent any
  stages {
    stage('检出代码') {
      steps {
        checkout([
          $class: 'GitSCM',
          branches: [[name: GIT_BUILD_REF]],
          extensions: [[$class: 'CloneOption', depth: 1, noTags: true, shallow: true]],
          userRemoteConfigs: [[
            url: GIT_REPO_URL,
            credentialsId: CREDENTIALS_ID
          ]]])
        }
      }
      stage('构建制品') {
        steps {
          sh "python3 setup.py sdist"
          sh "twine upload -r coding-pypi dist/*"
        }
      }
    }
  }
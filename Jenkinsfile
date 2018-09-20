pipeline {
  agent any
    
  tools {nodejs "node"}
    
  stages {
        
    stage('Cloning Git') {
      steps {
        git 'https://github.com/naveenkumarmarri/autobots.git'
      }
    }
        
    stage('Install dependencies') {
      steps {
	      dir('ui') {
	           sh 'npm install'  
     	  }
      }
    }
     
    stage('Test') {
      steps {
	     dir('ui') {
             sh 'npm test'
		 }
      }
    }      
  }
}

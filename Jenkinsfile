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
         sh 'ls'
	      dir('ui') {
               sh 'ls'
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

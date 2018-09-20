pipeline {
  agent any
    
  //tools {nodejs "node"}
    
  stages {
        
    stage('Install dependencies') {
      steps {
	      dir('ui') {
               sh 'ls'
	           sh 'npm install'  
     	  }
      }
    }
     
    /*stage('Test') {
      steps {
	     dir('ui') {
             sh 'npm test'
		 }
      }
    } */     
  }
}

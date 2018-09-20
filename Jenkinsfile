pipeline {
  agent any
    
  tools {nodejs "node"}
    
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
    stage('Pull Images') {
        steps {
		   sh 'chown $USER:$USER -R .'
		   sh 'docker-compose -f docker-compose.yml up -d' 
		}
    }
	stage('Test images'){
		steps{
			sh ' docker-compose exec broker kafka-topics --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 1 --topic trump'
		}
	}
	stage('Prune images'){
		imagePrune()
	}
  }

def imagePrune(){
    try {
 	    sh 'docker stop $(docker ps -aq)'        
 		sh 'docker rm $(docker ps -aq)'
 		sh 'docker rmi $(docker images -q)'
 
    } catch(error){}
}
}

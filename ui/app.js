var express=require('express');
var http=require('http');
var path=require('path');
var favicon=require('serve-favicon');
var bodyParser=require('body-parser');
var app=express();
// var dataGenerator=require('./randomDataGeneration')
var kafka = require('kafka-node');
var zkServer='localhost:2181'
var kafka_client_id='reporting_layer'
var kafkaClient=new kafka.Client(zkServer,kafka_client_id)
var consumer=new kafka.Consumer(kafkaClient,[{topic:'trump'}])

app.set('port',process.env.PORT || 5000);
// app.use(express.favicon());
// app.use(express.logger('dev'));
app.set('views', path.join(__dirname, 'views'));
app.engine('html', require('ejs').renderFile);
app.set('view engine', 'html');
app.use(bodyParser.json());
// app.use(bodyParser.urlencoded());
// app.use(express.methodOverride());

app.use(express.static(path.join(__dirname, 'public')))

// app.use(favicon(path.join(__dirname,'favicon.ico')));


var server=http.createServer(app).listen(app.get('port'),function () {
	// body...
	console.log('Express server listening on port:'+app.get('port'));
});
var io = require('socket.io')(server);

app.get('/',function(req,res){
	// console.log("Index");
	res.render('plot.html');
});

app.get('/socket',function(req,res){
	res.render('socket.html');
});

app.get('/plot',function(req,res){
	res.render('plot.html');
})

app.get('/line',function(req,res){
	res.render('lineChart.html');
})

// var io=require('socket.io').listen(server);
// io.sockets.on('connection',function(socket){
// 	socket.emit('message',{content:'You are connected!',importance:1});

// 	socket.on('message',function(message){
// 		console.log('Client has sent a message:'+message);
// 	});
// });


// io.sockets.on('connection',function(socket){
// 	var interval=setInterval(function(){
// 		var randomData=dataGenerator.getRandomData();
// 		socket.emit('dataSet',randomData);
// 	},1);
// 	socket.on('updateInterval',function(intervalData){
// 		clearInterval(interval);
// 		interval=setInterval(function(){
// 			var randomData=dataGenerator.getRandomData();
// 			socket.emit('dataSet',randomData);
// 		},intervalData);
// 	});
// });
// const consumer = new Kafka.SimpleConsumer

// var data=function(messageSet,topic,partition){
// 	messageSet.forEach(function(m){
// 		var res=[]
// 		var message=JSON.parse(m.message.value.toString("utf8"));
// 		res.push([message.x,message.y]);
// 		console.log(res)
// 		io.sockets.on('connection',function(socket){
// 			socket.emit('dataSet',res);
// 		});
// 	});
// }

// return consumer.init().then(function(){
// 	return consumer.subscribe('sample',data);
// });

consumer.on('message',function(message){
	//console.log(message.value);
	io.emit('dataSet',message.value);
});



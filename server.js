const tus = require('tus-node-server');
const express = require('express');
const server = new tus.Server();
server.datastore = new tus.FileStore({
    path: '/files'
});

const app = express();
const uploadApp = express();
uploadApp.all('*', server.handle.bind(server));
app.use('/uploads', uploadApp);

const host = '127.0.0.1';
const port = 8000;

// app.all('/files/*',function(req,res){
// 	server.handle(req,res);

// });

app.listen(port,()=>{
console.log(`[${new Date().toLocaleTimeString()}] tus server listening at http://${host}:${port}`);
});

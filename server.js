const tus = require('tus-node-server');
const EVENTS = require('tus-node-server').EVENTS
const express = require('express');
var contentDisposition = require('content-disposition')
var path = require('path');
var mime = require('mime');
var fs = require('fs');
const server = new tus.Server();

server.datastore = new tus.FileStore({
    path: '/files'
});

server.on(EVENTS.EVENT_ENDPOINT_CREATED, (event) => {
    console.log(event);
    console.log(`End point created: ${event.url}`);
});


const app = express();
const uploadApp = express();

uploadApp.all('/*', server.handle.bind(server));

app.use('/check',function(req,res){
    // console.log('Hello from Tus server');
    res.send('Tus server running');
});
// app.use('/uploads/files/*',function (req,res) {
//     res.send("Download not ready");
// });


app.use('/uploads', uploadApp);
app.use('/downloads',function (req,res) {
    console.log("Inside the downlaod api");
    var fileName=req.fileName;
    var file=__dirname+'/files/'+req.url.split('?')[0].split('/')[2];
    res.setHeader('Content-disposition', 'attachment; filename=' + req.query.fileName);
    var filestream = fs.createReadStream(file);
    filestream.pipe(res);
});



const host = '127.0.0.1';
const port = 8000;

app.listen(port,()=>{
console.log(`[${new Date().toLocaleTimeString()}] tus server listening at http://${host}:${port}`);
});

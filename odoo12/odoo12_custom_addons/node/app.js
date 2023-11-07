// -*- coding: utf-8 -*-
const http = require('http');
var express = require('express');
var app = express();
var bodyParser = require('body-parser');

app.use(bodyParser.json({limit: '500mb'}));
app.use(bodyParser.urlencoded({limit: '500mb', extended: true}));

var port = process.argv[2] ? process.argv[2] : 3000;
app.use(bodyParser.urlencoded({extended: false }));
app.use(bodyParser.json());

app.post('/', function (req, res) {
	console.log("hellp",req.body['printer'])
    var spawn = require("child_process").spawn;
    var pythonProcess = spawn('python3',["cups_direct_printing.py",req.body['data'],req.body['printer']], {
			detached: true,
			stdio: 'ignore'
		});
    setTimeout(function (){
    	console.log("process kill")
      	pythonProcess.kill();
      	pythonProcess.unref();
    },1000);
    // More of returning call
    // pythonProcess.stdout.on('data', function (data){
    //    res.send(data);
    // });

});

app.listen(port, function () {
  console.log('listening on port '+port+'!');
});

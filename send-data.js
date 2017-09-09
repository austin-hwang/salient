var http = require('http');
var express = require('express');
var bodyParser = require('body-parser');
var request = require('request');
var PythonShell = require('python-shell');
var cors = require('cors');
var argument = '';
var options = {
    mode: 'json',
    pythonPath: 'python3',
    args: [argument]
}
var dataSet = '';
var app = express();
app.set('port', process.env.PORT || 1234);

http.createServer(app).listen(app.get('port'), function () {
     console.log('Express server listening on port ' + app.get('port'));
});
  
app.get("/send-data", function (req, res) {
    console.log("working");
    sendData(req, res);
});

app.use(bodyParser.urlencoded({
    extended: true
  }), bodyParser.json(), function (req, res, next) {
    res.header('Content-Type', 'application/json');
    res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', "Origin, X-Requested-With, Content-Type, Accept");
    res.setHeader('Access-Control-Allow-Credentials', true);
    next();
  });

app.post("/send-argument", function (req, res) {
    argument = req.body.title;
});

var sendData = (req, res) => {
    res.header('Content-Type', 'application/json');
    res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', "Origin, X-Requested-With, Content-Type, Accept");
    res.setHeader('Access-Control-Allow-Credentials', true);
  
    PythonShell.run('digest.py', options, function (err, results) {
        if (err) throw err;
        // results is an array consisting of messages collected during execution
        //res.send(results);
        dataSet = results[0];
        res.send(results[0]);
        //res.send(dataSet.news[0].url);
      });
};

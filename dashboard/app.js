
/**
 * Module dependencies.
 */

var express = require('express')
  , routes = require('./routes')
  , user = require('./routes/user')
  , users = require('./routes/users')
  , fetch = require('./routes/fetch')
  , http = require('http')
  , cluster = require('cluster')
  , swig = require('swig')
//  , cluster = require('cluster')
  , path = require('path');

swig.init({ root: __dirname + '/views', allowErrors: true, filters: require('./dataviz_filters') });

var app = express();

app.configure(function(){
  app.set('port', process.env.PORT || 3000);
  app.set('views', __dirname + '/views');
  app.set('view engine', 'html');
  app.use(express.favicon());
  app.use(express.logger('dev'));
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(app.router);
  app.use(express.static(path.join(__dirname, 'public')));
});

app.configure('development', function(){
  app.use(express.errorHandler());
});

app.get('/', routes.index);
app.get('/users', users.index);
app.get('/user/:id', user.view);
app.get('/fetch', fetch.fetch_data);

// var numWorkers = 5;

/* if (cluster.isMaster) {
    for (var i = 0; i < numWorkers; i++) {
        cluster.fork();
    }
} else {

} */

http.createServer(app).listen(app.get('port'), function(){
    console.log("Express server listening on port " + app.get('port'));
});

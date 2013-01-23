var swig  = require('swig'); 
var cluster = require('cluster');
var sleep = require('sleep');

/*
 * GET home page.
 */

exports.index = function(req, res) {
    var tmpl = swig.compileFile('index.html');

    res.send(tmpl.render({ title: 'Express' }));

//    console.log('I am worker #' + cluster.worker.id);
};

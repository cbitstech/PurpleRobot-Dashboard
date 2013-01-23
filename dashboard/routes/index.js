var swig  = require('swig'); 
var cluster = require('cluster');

/*
 * GET home page.
 */

exports.index = function(req, res) {
    var tmpl = swig.compileFile('index.html');

    res.send(tmpl.render({ title: 'Express' }));
};

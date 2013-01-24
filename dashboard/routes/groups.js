var swig  = require('swig'); 

exports.index = function(req, res)
{
    var tmpl = swig.compileFile('index.html');

    res.send(tmpl.render({ title: 'Express' }));
};

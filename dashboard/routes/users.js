var swig  = require('swig'); 
var database = require('../database');

exports.index = function(req, res)
{
    var tmpl = swig.compileFile('users.html');
    
    database.fetchDatabases(function databasesCallback(databases)
    {
        res.send(tmpl.render({ databases: databases }));
    });
};

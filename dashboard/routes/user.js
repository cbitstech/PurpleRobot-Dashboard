var swig  = require('swig'); 
var database = require('../database');

exports.view = function(req, res)
{
    var tmpl = swig.compileFile('user.html');
      
    database.fetchDatabase(req.params.id, function userCallback(user)
    {
        database.fetchDatabases(function databasesCallback(databases)
        {
            res.send(tmpl.render({ user: user, databases: databases }));
        });
    });
};

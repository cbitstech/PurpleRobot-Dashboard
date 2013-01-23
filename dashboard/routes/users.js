var swig  = require('swig'); 
var cluster = require('cluster');
var database = require('../database');
/*
 * GET home page.
 */

exports.index = function(req, res) {
    var tmpl = swig.compileFile('users.html');
    
    database.fetchDatabases(function databasesCallback(databases)
    {
        console.log(JSON.stringify(databases));
        
        // PARALLELIZE!
        res.send(tmpl.render({ databases: databases }));
    });
};

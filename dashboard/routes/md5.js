var swig  = require('swig'); 
var database = require('../database');
var crypto = require('crypto');

exports.index = function(req, res)
{
    var tmpl = swig.compileFile('md5.html');
    
    res.send(tmpl.render({}));
};

exports.lookup = function(req, res)
{
    var tmpl = swig.compileFile('md5_lookup.html');
    
    var identifiers = req.body.identifiers.replace(/(\r\n|\n|\r)/gm, '\n').split('\n');

    database.fetchDatabases(function databasesCallback(databases)
    {
        var results = [];
        
        var i = 0;
        
        for (var i = 0; i < identifiers.length; i++)
        {
            var hash = crypto.createHash('md5');
            
            var identifier = identifiers[i].trim();
            
            if (identifier.length > 0)
            {
                hash.update(identifier, 'utf8');
                
                var result = {};
                
                result.identifier = identifier;
                result.hash = hash.digest('hex');
                
                if (databases.indexOf(result.hash) != -1)
                    result.found = true;
                else
                    result.found = false;
                
                results.push(result);
            }
        }
        
        res.send(tmpl.render({ results: results }));
    });
};

var url = require('url')

var db = require('../database');

exports.fetch_data = function(req, res)
{
    var params = url.parse(req.url, true);
  
    var database = params.query.database;
    var table = params.query.table;
    var timestamp = params.query.timestamp;
    var columns = [];
    
    var tokens = params.query.columns.split(',');
    var i = 0;
   
    for (i = 0; i < tokens.length; i++)
        columns.push(tokens[i]);
    
    db.fetchReadings(database, table, columns, timestamp, function readingsFetched(database, table, readings)
    {
        res.setHeader('Content-Type', 'application/json');
        res.send(JSON.stringify(readings));
    },
    function readingsError(err)
    {
        res.send(JSON.stringify(err));
    });
};

var pg = require('pg');
var async = require('async');
var charts = require('./charts');

var username = "postgres";
var password = "mohrLab1";
var host = "165.124.171.126";

exports.fetchDatabases = function(callback)
{
    var connectionString = "pg://" + username + ":" + password + "@" + host + "/postgres";

    pg.connect(connectionString, function(err, client)
    {
        var query = "SELECT datname FROM pg_database;"
        
        client.query(query, function(err, result)
        {
            var databases = [];
            
            for (var i = 0; i < result.rows.length; i++)
            {
                if (result.rows[i].datname.length > 16)
                {
                    databases.push(result.rows[i].datname);
                }
            }
            
            callback(databases);
        });
    });
};

exports.fetchColumns = function(database, table, callback)
{
    var connectionString = "pg://" + username + ":" + password + "@" + host + "/" + database;

    pg.connect(connectionString, function(err, client)
    {
        var query = "SELECT column_name,data_type FROM information_schema.columns WHERE table_name = '" + table + "';";
        
        client.query(query, function(err, result)
        {
            var columns = [];
            
            for (var i = 0; i < result.rows.length; i++)
            {
                var column = {};
                column.name = result.rows[i].column_name;
                column.type = result.rows[i].data_type;
                
                columns.push(column);
            }
            
            if (callback !== null)
                callback(columns);
        });
    });
};

function makeColumnsCallback(database, table)
{
    return function(callback)
    {
        exports.fetchColumns(database, table, function(columns)
        {
            var tableColumns = { name: table, columns: [] };
            
            for (var i = 0; i < columns.length; i++)
                tableColumns.columns.push(columns[i]);
            
            callback(null, tableColumns);
        });
    };
};

exports.values = function(database, table, columns, callback)
{
    var connectionString = "pg://" + username + ":" + password + "@" + host + "/" + database;
    
    pg.connect(connectionString, function(err, client)
    {
        var query = "SELECT * FROM \"" + table + "\" LIMIT 1000;";
        
        client.query(query, function(err, result)
        {
            var data = [];

            for (var i = 0; i < result.rows.length; i++)
            {
                var rowData = [];
                
                for (var j = 0; j < columns.length; j++)
                {
                    rowData.push(result.rows[i][columns[j]]);
                }
                
                data.push(rowData);
            }
            
            callback(data);
        });
    });
};

exports.fetchDatabase = function(database, callback)
{
    var connectionString = "pg://" + username + ":" + password + "@" + host + "/" + database;

    pg.connect(connectionString, function(err, client)
    {
        var query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';";
        
        client.query(query, function(err, result)
        {
            var ops = [];
            
            for (var i = 0; i < result.rows.length; i++)
            {
                var op = makeColumnsCallback(database, result.rows[i].table_name);
                
                ops.push(op);
            }
            
            var dbObj = {};
            dbObj["id"] = database;
            
            async.parallel(ops, function(err, results)
            {
                var tables = [];
                
                for (var i = 0; i < results.length; i++)
                {
                    results[i].database = database;
                    tables.push(charts.chartForObject(results[i].name, results[i]));
                }
                
                dbObj["tables"] = tables;
                
                callback(dbObj);
            });
        });
    });
}

exports.fetchReadings = function(database, table, columns, timestamp, callback, error)
{
    var connectionString = "pg://" + username + ":" + password + "@" + host + "/" + database;

    pg.connect(connectionString, function(err, client)
    {
        // TODO: Find a ANY way to protect against SQL injection...
        
        var tableList = '"timestamp"';
        
        var i = 0;
        for (i = 0; i < columns.length; i++)
        {
            tableList += ',';
            tableList += '"' + columns[i] + '"';
        }
        
        var sql = 'WITH t AS (SELECT ' + tableList + ' FROM "' + table + '" ORDER BY "' + timestamp + '" DESC LIMIT 500) SELECT * FROM t ORDER BY "' + timestamp + '" ASC;';
        
        console.log('SQL: ' + sql);
        
        var query = client.query(sql);
        
        var readings = [];
        
        var lastReading = {};
        var lastTimestamp = 0;
        
        query.on('row', function rowFetched(row)
        {
            var reading = {};
            
            reading['timestamp'] = row[timestamp];
            
            var isSame = true;
            
            var i = 0;
            for (i = 0; i < columns.length; i++)
            {
                reading[columns[i]] = row[columns[i]];
                
                if (reading['timestamp'] - lastTimestamp > 1000)
                    isSame = false;
                
                if (lastReading[columns[i]] !== reading[columns[i]])
                    isSame = false;
                    
                lastReading[columns[i]] = reading[columns[i]];
            }
            
            if (isSame === false)
            {
                readings.push(reading);
                lastTimestamp = reading['timestamp'];
            }
        });
        
        query.on('end', function rowsFetched(result)
        {
            client.end.bind(client)
            
            callback(database, table, readings);
        });
    });
};

var db = require('../database');

db.fetchDatabases(function generateReport(databases)
{
    var i = 0;
    for (i = 0; i < databases.length; i++)
    {
        var database = databases[i];
        
        db.fetchReadings(database, 'BatteryProbe', ['level'], 'timestamp', function readingsFetched(database, table, readings)
        {
            console.log(database + ': ' + JSON.stringify(readings.length));
        });
    }
});

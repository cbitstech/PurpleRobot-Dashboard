import collections
import datetime
import psycopg2

IGNORE = ['SourceValue'];

def database_exists(database):
    try:
        db_string = 'host=\'165.124.171.126\' dbname=\'' + database + '\' user=\'postgres\' password=\'mohrLab1\''
        conn = psycopg2.connect(db_string)
        cursor = conn.cursor()

        cursor.close()
        conn.close()
        
        return True
    except:
        pass
        
    return False

def table_exists(database, table_name):
    db_string = 'host=\'165.124.171.126\' dbname=\'' + database + '\' user=\'postgres\' password=\'mohrLab1\''
    conn = psycopg2.connect(db_string)
    cursor = conn.cursor()
        
    exists = False

    try:
        cursor.execute('SELECT * FROM "' + table_name + '" ;')
        exists = True   
    except:
        pass
        
    conn.close()
    cursor.close()
        
    return exists

def fetch_columns(database, table):
    db_string = 'host=\'165.124.171.126\' dbname=\'' + database + '\' user=\'postgres\' password=\'mohrLab1\''
    conn = psycopg2.connect(db_string)
    cursor = conn.cursor()
        
    columns = []

    try:
        cursor.execute('SELECT column_name,data_type FROM information_schema.columns WHERE table_name = \'' + table + '\';')
        
        for result in cursor:
            columns.append((result[0], result[1]))
    except:
        pass

    conn.close()
    cursor.close()
    
    return columns

def fetch_tables(database):
    db_string = 'host=\'165.124.171.126\' dbname=\'' + database + '\' user=\'postgres\' password=\'mohrLab1\''
    conn = psycopg2.connect(db_string)
    cursor = conn.cursor()
        
    tables = []

    try:
        cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\';')

        for result in cursor:
            if result[0] in IGNORE:
                pass
            else:
                table = {}
                table['name'] = result[0]
                table['columns'] = fetch_columns(database, table['name'])
                table['database'] = database
                tables.append(table)
    except:
        pass
        
    conn.close()
    cursor.close()

    tables = sorted(tables, key=lambda x: x['name'].lower())
    
    return tables


def fetch_data(database, table_name, column_name, start=datetime.datetime.min, end=datetime.datetime.max, distinct=False, limit=0):
    db_string = 'host=\'165.124.171.126\' dbname=\'' + database + '\' user=\'postgres\' password=\'mohrLab1\''
    conn = psycopg2.connect(db_string)
    cursor = conn.cursor()

    values = []
    
    try:
        query = 'SELECT "eventDateTime","' + column_name + '" FROM "' + table_name + '" WHERE ("eventDateTime" >= %s AND "eventDateTime" <= %s)'
        
        if distinct:
            query = 'SELECT DISTINCT "' + column_name + '" FROM "' + table_name + '" WHERE ("eventDateTime" >= %s AND "eventDateTime" <= %s)'
            
        if limit > 0:
            query += 'ORDER BY "eventDateTime" DESC LIMIT ' + str(limit)
            
        query += ';'

        cursor.execute(query, (start, end,))
        
        for result in cursor:
            if len(result) >= 2:
                values.append([result[0], result[1]])
            else:
                values.append([0, result[0]])
    except:
        pass
        
    conn.close()
    cursor.close()
    
    return list(reversed(values))

def all_databases():
    db_string = 'host=\'165.124.171.126\' dbname=\'postgres\' user=\'postgres\' password=\'mohrLab1\''

    conn = psycopg2.connect(db_string)
    
    cursor = conn.cursor()
    
    cursor.execute('SELECT datname FROM pg_database;')
    
    databases = []
    
    for result in cursor:
        if len(result[0]) > 16:
            databases.append(result[0])
    
    cursor.close()
    conn.close()
    
    return databases

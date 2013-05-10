import psycopg2

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


def fetch_data(database, table_name, column_name, start, end, distinct=False):
    db_string = 'host=\'165.124.171.126\' dbname=\'' + database + '\' user=\'postgres\' password=\'mohrLab1\''
    conn = psycopg2.connect(db_string)
    cursor = conn.cursor()

    values = []
    
    try:
        query = 'SELECT "eventDateTime","' + column_name + '" FROM "' + table_name + '" WHERE ("eventDateTime" >= %s AND "eventDateTime" <= %s);'
        
        if distinct:
            query = 'SELECT DISTINCT "' + column_name + '" FROM "' + table_name + '" WHERE ("eventDateTime" >= %s AND "eventDateTime" <= %s);'

        cursor.execute(query, (start, end,))
        
        for result in cursor:
            if len(result) >= 2:
                values.append((result[0], result[1],))
            else:
                values.append((0, result[0],))
    except:
        pass
        
    conn.close()
    cursor.close()
        
    return values

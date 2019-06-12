import json
import sys
import psycopg2

from api import API

error_function = lambda *_, **__: ("ERROR", None)

def init_database(cursor):
    with open('initialize_tables.sql', 'r') as f:
        cursor.execute(f.read())
    with open('initialize_app.sql', 'r') as f:
        cursor.execute(f.read())

def get_input(line):
    return list(json.loads(line).items())[0]

def get_connection(database, login, password):
    connection = psycopg2.connect(dbname=database, user=login, password=password)
    return connection

if __name__ == '__main__':
    for line in sys.stdin:
        try:
            function, kwargs = get_input(line)
        except:
            continue

        if function == 'open':
            api = None
            try:
                connection = get_connection(**kwargs)
                if '--init' in sys.argv:
                    init_database(connection.cursor())
                api = API(connection)
                print(json.dumps({"status": "OK"}))
            except:
                print(json.dumps({"status": "ERROR"}))
            
        else:
            status, data = getattr(api, function, error_function)(**kwargs)
            print(json.dumps({field: value for field, value in zip(["status", "data"], [status, data]) if value is not None}))

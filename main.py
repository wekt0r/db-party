import json
import sys
from typing import Tuple, Dict
import psycopg2

from api import API

error_function = lambda *_, **__: ("ERROR", None)

def init_database(cursor):
    with open('initialize_tables.sql', 'r') as f:
        cursor.execute(f.read())
    #with open('initialize_app.sql', 'r') as f:
    #    cursor.execute(f.read())

def get_input():
    try:
        return list(json.loads(input()).items())[0]
    except:
        exit()

def get_connection(database, login, password):
    connection = psycopg2.connect(dbname=database, user=login, password=password)
    connection.set_session(autocommit=True)
    return connection

if __name__ == '__main__':
    while True:
        function, kwargs = get_input()
        if function == 'open':
            connection = get_connection(**kwargs)
            if '--init' in sys.argv:
                init_database(connection.cursor())
            api = API(connection.cursor())
            
        else:
            status, data = getattr(api, function, error_function)(**kwargs)
            print(f'made {status} with {data}')
            print(json.dumps({field: value for field, value in zip(["status", "data"], [status, data]) if value}))
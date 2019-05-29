import json
import sys
from typing import Tuple, Dict

from api import Database

def init_database():
    pass

def get_input() -> Tuple[str, Dict] :
    try:
        return list(json.loads(input()).items())[0]
    except:
        print("sth went wrong")


if __name__ == '__main__':
    if '--init' in sys.argv:
        init_database()

    while(True):
        function, kwargs = get_input()
        if function == 'open':
            db = Database(**kwargs)
        
        else:
            status, data = db.perform(function, kwargs)
            print(json.dumps({"status": status,
                              "data": data}))
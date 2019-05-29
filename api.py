"""

open <database> <login> <password>

leader <password> <member>

---

support <timestamp> <member> <password> <action> <project> [ <authority> ]

protest <timestamp> <member> <password> <action> <project> [ <authority> ]

-

upvote <timestamp> <member> <password> <action> 

downvote <timestamp> <member> <password> <action> 

-

actions <timestamp> <member> <password> [ <type> ] [ <project> | <authority> ]

projects <timestamp> <member> <password> [ authority ]

votes <timestamp> <member> <password> [ <action> | <project> ]

trolls (funkcja bez parametrów)

"""
import psycopg2
from collections import namedtuple

VALIDATE_QUERY = "SELECT password = crypt(%s, password), role FROM member WHERE id=%s;"
LEADER_QUERY = "INSERT INTO member VALUES (%s, crypt(%s, gen_salt(\'bf\')), \'leader\', now());"
SUPPORT_OR_PROTEST_QUERY = "INSERT INTO action VALUES(%s,%s,%s,%s, 0);"
VOTE_QUERY = "INSERT INTO member_votes_for_action VALUES (%s,%s, %s);"

ValidationTuple = namedtuple("ValidationTuple", ["is_login_successful","role"]) 

class Database:
    def __init__(self, database, login, password):
        self.__connection = psycopg2.connect(dbname=database, user=login, password=password)
        self.cursor = self.__connection.cursor()
        self.FUNCTIONS = {
            'open':     self._open,
            'leader':   self._leader,
            'support':  self._support,
            'protest':  self._protest,
            'upvote':   self._upvote,
            'actions':  self._actions,
            'projects': self._projects,
            'votes':    self._votes,
            'trolls':   self._trolls}

    def __validate_user(self, member: int, password: str):
        self.cursor.execute(VALIDATE_QUERY, (password, member)) #maybe add timestamp here, so we can check rn if timestamp - last_activity > 1year and set it away"
        return ValidationTuple(*self.cursor.fetchone()[0])

    def _open(self, password: str, member: int):
        pass

    def _leader(self, password: str, member: int):
        self.cursor.execute()
        pass

    def _support(self, timestamp: int, member: int, password: str, action: int, project: int, authority: int = None):
        pass

    def _protest(self, timestamp: int, member: int, password: str, action: int, project: int, authority: int = None): 
        pass

    def _upvote(self, timestamp: int, member: int, password: str, action: int):
        pass

    def _downvote(self, timestamp: int, member: int, password: str, action: int):
        pass

    def __gen_actions_string(*args):
        return "SELECT a.id, a.action, a.project_id, p.authority_id, a.upvotes, a.downvotes FROM action a JOIN project p ON(p.id = a.project_id) {} ORDER BY a.id;".format(
                "WHERE" + " AND ".join([f'{arg}=%s' for arg in args if arg])
                ) 
        

    def _actions(self, timestamp: int, member: int, password: str, type: str = None, project: int = None, authority: int = None):
        
        self.cursor.execute(__gen_actions_string(type, project, authority), filter(lambda x: x, [type, project, authority]))
        #"SELECT a.id, a.action, a.project_id, p.authority_id, a.upvotes, a.downvotes FROM action a JOIN project p ON(p.id = a.project_id) WHERE {} ORDER BY a.id;" 
        "// <action> <type> <project> <authority> <upvotes> <downvotes>"
        pass

    def _projects(self, timestamp: int, member: int, password: str, authority: int = None):
        f'SELECT'
        "// <project> <authority>"
        pass

    def _votes(self, timestamp: int, member: int, password: str, action: int = None, project: int = None):
        f'SELECT member_id, COUNT(*) FROM member LEFT JOIN member_votes_for_action ON (id = member_id) GROUP BY member_id, vote_type;'

    def _trolls(self):
        f'SELECT DISTINCT (member_id) FROM actions WHERE vote_status < 0;'
        pass

    def perform(self, function, kwargs):
        if function in self.FUNCTIONS:
            self.FUNCTIONS[function](**kwargs)
            

from collections import namedtuple

VALIDATE_QUERY = "SELECT password = crypt(%(password)s, password), role, to_timestamp(%(timestamp)s) - last_activity > INTERVAL '1 year' FROM member WHERE id=%(member)s;"
LEADER_QUERY = "INSERT INTO member(id, password, role_group, last_activity) VALUES (%(member)s, crypt(%(password)s, gen_salt(\'bf\')), \'leader\', %(timestamp)s);"
SUPPORT_OR_PROTEST_QUERY = "INSERT INTO action(id,project_id, member_id, action) VALUES(%(action)s,%(project)s,%(member)s,%(action_type)s);"
VOTE_QUERY = "INSERT INTO member_votes_for_action VALUES (%(member)s,%(action)s, %(vote)s);"
ACTIONS_QUERY = "SELECT a.id, a.action, a.project_id, p.authority_id, a.upvotes, a.downvotes FROM action a JOIN project p ON(p.id = a.project_id) {} ORDER BY a.id;"
PROJECTS_QUERY = "SELECT id as project, authority_id as authority FROM project {} ORDER BY id ASC;"

VOTES_QUERY = """SELECT member.id, coalesce(upvotes, 0) as upvotes, coalesce(downvotes,0) as downvotes FROM member 
	LEFT JOIN (SELECT member_id, COUNT(*) AS upvotes FROM member_votes_for_action WHERE vote='upvote' {} GROUP BY member_id) up ON (up.member_id=id)
	LEFT JOIN (SELECT member_id, COUNT(*) AS downvotes FROM member_votes_for_action WHERE vote='downvote' {} GROUP BY member_id) down ON(id = down.member_id);"""

TROLLS_QUERY = """SELECT id as member, upvotes, downvotes, to_timestamp(%(timestamp)s) - last_activity <= INTERVAL '1 year' as active FROM member WHERE upvotes - downvotes < 0 ORDER BY upvotes - downvotes DESC, member ASC;"""

ValidationTuple = namedtuple("ValidationTuple", ["is_successful","role"]) 
ResultTuple = namedtuple("ResultTuple", ["status", "data"])            

def validator(needed_role):
    def wrap(f):
        def validator_decorator(self, *args, **kwargs):
            validation = self._validate_user(kwargs['member'], kwargs['password'], kwargs['timestamp'])
            if validation.is_successful and validation.role == needed_role:
                return self.func(*args, **kwargs)
            else:
                return "ERROR", None
        return validator_decorator
    return wrap


class API:
    def __init__(self, cursor_to_db):
        self.cursor = cursor_to_db
        
    def _validate_user(self, member: int, password: str, timestamp: int) -> ValidationTuple:
        self.cursor.execute(VALIDATE_QUERY, {'password': password, 
                                             'timestamp': timestamp, 
                                             'member': member}) 
        return ValidationTuple(*self.cursor.fetchone()[0])

    def leader(self, timestamp: int, password: str, member: int):
        self.cursor.execute(LEADER_QUERY, (member, password, timestamp))
        pass

    @validator("member")
    def support(self, timestamp: int, member: int, password: str, action: int, project: int, authority: int = None):
        self.cursor.execute(SUPPORT_OR_PROTEST_QUERY, {'member': member, 'project': project,
                                                       'action': action, 'action_type': 'support'})

    @validator("member")
    def protest(self, timestamp: int, member: int, password: str, action: int, project: int, authority: int = None): 
        self.cursor.execute(SUPPORT_OR_PROTEST_QUERY, {'member': member, 'project': project,
                                                       'action': action, 'action_type': 'protest'})

    @validator("member")
    def upvote(self, timestamp: int, member: int, password: str, action: int):
        self.cursor.execute(VOTE_QUERY, {'member': member,'action': action, 'vote': 'upvote'})

    @validator("member")
    def downvote(self, timestamp: int, member: int, password: str, action: int):
        self.cursor.execute(VOTE_QUERY, {'member': member,'action': action, 'vote': 'downvote'})

    def __gen_conditional_string(self, query, *args):
        return query.format(
                ("WHERE " if any(args) else "") + " AND ".join([f'{arg}=%s' for arg in args if arg])) 
        
    @validator("leader")
    def actions(self, timestamp: int, member: int, password: str, type: str = None, project: int = None, authority: int = None):
        self.cursor.execute(self.__gen_conditional_string(ACTIONS_QUERY, type, project, authority), filter(lambda x: x, [type, project, authority]))
        return self.cursor.fetchall()

    @validator("leader")
    def projects(self, timestamp: int, member: int, password: str, authority: int = None):
        self.cursor.execute(self.__gen_conditional_string(PROJECTS_QUERY,authority), filter(lambda x: x, [authority]))
        return self.cursor.fetchall()

    def __gen_votes_string(self, *args):
        return VOTES_QUERY.format(
                ("AND " if any(args) else "") + " AND ".join([f'{arg}=%s' for arg in args if arg])) 

    @validator("leader")
    def votes(self, timestamp: int, member: int, password: str, action: int = None, project: int = None):
        self.cursor.execute(self.__gen_votes_string(action, project), tuple(filter(lambda x: x, [action, project])))
        return self.cursor.fetchall()

    @validator("leader")
    def trolls(self, timestamp: int):
        self.cursor.execute(TROLLS_QUERY, (timestamp,) )
        return self.cursor.fetchall()
            

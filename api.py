from collections import namedtuple

import queries

ValidationTuple = namedtuple("ValidationTuple", ["is_successful", "role", "inactive"]) 

def validator(needed_role, should_insert=False):
    def wrap(func):
        def validator_decorator(self, *args, **kwargs):
            validation = self._validate_user(kwargs['member'], kwargs['password'], kwargs['timestamp'])
            if not validation and should_insert:
                self.cursor.execute(queries.MEMBER_INSERT_QUERY, {**kwargs, 'role': 'member'})
                validation = ValidationTuple(True, "member", False)
            if validation.is_successful and not validation.inactive and validation.role in [needed_role, 'leader']:
                try:
                    result = ("OK", func(self, *args, **kwargs))
                    self.cursor.execute(queries.UPDATE_TIMESTAMP_QUERY, {'member': kwargs['member'], 
                                                                         'timestamp': kwargs['timestamp']})
                    self.connection.commit()                                                     
                    return result
                except:
                    self.connection.rollback()
                    return ("ERROR", None)
            else:
                self.connection.rollback()
                return ("ERROR", None)
        return validator_decorator
    return wrap


class API:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        
    def _validate_user(self, member: int, password: str, timestamp: int) -> ValidationTuple:
        self.cursor.execute(queries.VALIDATE_QUERY, {'password': password, 
                                                     'timestamp': timestamp, 
                                                     'member': member})
        try:
            return ValidationTuple(*self.cursor.fetchone())
        except:
            return None

    def leader(self, timestamp: int, password: str, member: int):
        try:
            self.cursor.execute(queries.MEMBER_INSERT_QUERY, {'member': member, 'password': password, 
                                                              'timestamp': timestamp, 'role': 'leader'})
            self.connection.commit()
            return ("OK", None)
        except:
            return ("ERROR", None)

    @validator("member", should_insert=True)
    def support(self, timestamp: int, member: int, password: str, action: int, project: int, authority: int = None):
        self.cursor.execute(queries.SUPPORT_OR_PROTEST_QUERY, {'member': member, 'project': project,
                                                               'action': action, 'action_type': 'support',
                                                               'authority': authority})

    @validator("member", should_insert=True)
    def protest(self, timestamp: int, member: int, password: str, action: int, project: int, authority: int = None): 
        self.cursor.execute(queries.SUPPORT_OR_PROTEST_QUERY, {'member': member, 'project': project,
                                                               'action': action, 'action_type': 'protest',
                                                               'authority': authority})

    @validator("member", should_insert=True)
    def upvote(self, timestamp: int, member: int, password: str, action: int):
        self.cursor.execute(queries.VOTE_QUERY, {'member': member,'action': action, 'vote': 'upvote'})

    @validator("member", should_insert=True)
    def downvote(self, timestamp: int, member: int, password: str, action: int):
        self.cursor.execute(queries.VOTE_QUERY, {'member': member,'action': action, 'vote': 'downvote'})

    def __gen_conditional_string(self, query, **kwargs):
        return query.format(
                ("WHERE " if any(kwargs.values()) else "") + " AND ".join([f'{k}=%({k})s' for k,v in kwargs.items() if v])) 
        
    @validator("leader")
    def actions(self, timestamp: int, member: int, password: str, type: str = None, project: int = None, authority: int = None):
        additional_kwargs = {'action': type, 'project_id': project, 'authority_id': authority}
        self.cursor.execute(self.__gen_conditional_string(queries.ACTIONS_QUERY, **additional_kwargs), additional_kwargs)
        return self.cursor.fetchall()

    @validator("leader")
    def projects(self, timestamp: int, member: int, password: str, authority: int = None):
        self.cursor.execute(self.__gen_conditional_string(queries.PROJECTS_QUERY, authority_id = authority), {'authority_id': authority})
        return self.cursor.fetchall()

    def __gen_votes_string(self, **kwargs):
        return queries.VOTES_QUERY.format(
                condition=("AND " if any(kwargs.values()) else "") + " AND ".join([f'{k}=%({k})s' for k,v in kwargs.items() if v]))

    @validator("leader")
    def votes(self, timestamp: int, member: int, password: str, action: int = None, project: int = None):
        self.cursor.execute(self.__gen_votes_string(action_id = action, project_id = project), {'action_id': action, 'project_id': project})
        return self.cursor.fetchall()

    def trolls(self, timestamp: int):
        self.cursor.execute(queries.TROLLS_QUERY, {'timestamp': timestamp} )
        return "OK", self.cursor.fetchall()
            

UPDATE_TIMESTAMP_QUERY = "UPDATE member SET last_activity=to_timestamp(%(timestamp)s) WHERE id=%(member)s;"

VALIDATE_QUERY = """SELECT password = crypt(%(password)s, password), 
                           role_group, 
                           to_timestamp(%(timestamp)s) - last_activity > INTERVAL '1 year' 
                    FROM member WHERE id=%(member)s;"""

MEMBER_INSERT_QUERY = """INSERT INTO member(id, password, role_group, last_activity) 
                        VALUES (%(member)s, crypt(%(password)s, gen_salt(\'bf\')), %(role)s, to_timestamp(%(timestamp)s));"""

SUPPORT_OR_PROTEST_QUERY = """INSERT INTO action(id,project_id, member_id, action) 
                              VALUES(%(action)s, check_project_id(%(project)s, %(authority)s), %(member)s, %(action_type)s);"""

VOTE_QUERY = """INSERT INTO member_votes_for_action 
                VALUES (%(member)s,%(action)s, %(vote)s);"""

# IMPORTANT NOTE: Having {} in queries below IS NOT vulnerable to sql injection
#   since {} is always formatted with constant values with %(name)s in it for appropriate variables.
#   This way we leave sanitization for execute function (which deals with sql injections according to documentation)   

ACTIONS_QUERY = """SELECT a.id, a.action, a.project_id, 
                          p.authority_id, a.upvotes, a.downvotes 
                   FROM action a JOIN project p ON(p.id = a.project_id) {} 
                   ORDER BY a.id ASC;"""

PROJECTS_QUERY = """SELECT id as project, authority_id as authority 
                    FROM project {} 
                    ORDER BY id ASC;"""

VOTES_QUERY = """SELECT member.id, 
                        coalesce(up.upvotes, 0) as upvotes, 
                        coalesce(down.downvotes,0) as downvotes 
                 FROM member 
                    LEFT JOIN (SELECT mva.member_id as member_id, COUNT(*) AS upvotes 
                               FROM member_votes_for_action mva JOIN action a ON (mva.action_id = a.id) 
                               WHERE mva.vote='upvote' {condition} 
                               GROUP BY mva.member_id) up ON (up.member_id=id)
	                LEFT JOIN (SELECT mva.member_id as member_id, COUNT(*) AS downvotes 
                               FROM member_votes_for_action mva JOIN action a ON (mva.action_id = a.id) 
                               WHERE mva.vote='downvote' {condition} 
                               GROUP BY mva.member_id) down ON(id = down.member_id) 
                 ORDER BY member ASC;"""

TROLLS_QUERY = """SELECT id as member, upvotes, downvotes, 
                         to_timestamp(%(timestamp)s) - last_activity <= INTERVAL '1 year' as active 
                  FROM member 
                  WHERE upvotes - downvotes < 0 
                  ORDER BY downvotes - upvotes DESC, member ASC;"""
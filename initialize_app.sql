CREATE USER app WITH ENCRYPTED PASSWORD 'qwerty';
GRANT CONNECT ON DATABASE student TO app;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app;
GRANT INSERT ON member, member_votes_for_action, action TO app;
GRANT UPDATE (last_activity) on member TO app;
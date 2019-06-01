echo '
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app;
GRANT INSERT ON member, member_votes_for_action, action TO app;
' | sudo -u postgres psql -d student;

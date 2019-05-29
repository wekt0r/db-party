BEGIN TRANSACTION;

CREATE TYPE role_type AS ENUM('leader', 'member', 'inactive');
CREATE TYPE action_type AS ENUM('protest', 'support');
CREATE TYPE vote_type AS ENUM('upvote', 'downvote');

CREATE OR REPLACE FUNCTION unique_ids(numeric) RETURNS boolean AS
$$
	DECLARE 
		row_count numeric;
	BEGIN
	SELECT COUNT(*) FROM ((SELECT id FROM member WHERE id=$1) UNION 
	(SELECT id FROM action WHERE id=$1) UNION
	(SELECT id FROM project WHERE id=$1) UNION
	(SELECT id FROM authority WHERE id=$1)) AS r INTO row_count;
	RAISE NOTICE 'Value: %', row_count;

	RETURN row_count = 0;
	END
$$ 
LANGUAGE plpgsql;

CREATE TABLE member (
	id numeric PRIMARY KEY CHECK(unique_ids(id)),
	password text,
	role_group role_type DEFAULT 'member',
	last_activity timestamp without time zone
);

CREATE TABLE authority (
	id numeric PRIMARY KEY CHECK(unique_ids(id))
);

CREATE TABLE project (
	id numeric PRIMARY KEY CHECK(unique_ids(id)),
	authority_id numeric REFERENCES authority(id)
);

CREATE TABLE action (
	id numeric PRIMARY KEY CHECK(unique_ids(id)),
	project_id numeric REFERENCES project(id),
	member_id numeric REFERENCES member(id) NOT NULL,
	action action_type NOT NULL,
	upvotes bigint DEFAULT 0,
        downvotes bigint DEFAULT 0	
);

CREATE TABLE member_votes_for_action (
	member_id numeric REFERENCES member(id),
	action_id numeric REFERENCES action(id),
	vote vote_type NOT NULL
);


CREATE OR REPLACE FUNCTION vote() RETURNS TRIGGER AS 
$$
BEGIN 
	IF NEW.vote='upvote' THEN
		UPDATE action SET upvotes = upvotes + 1 WHERE id = NEW.action_id;
	ELSE
		UPDATE action SET downvotes = downvotes + 1 WHERE id = NEW.action_id;
	END IF;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_vote AFTER INSERT ON member_votes_for_action FOR EACH ROW EXECUTE PROCEDURE vote();

-- CREATE OR REPLACE FUNCTION test() RETURNS bool AS

COMMIT;

BEGIN TRANSACTION;

CREATE TYPE role_type AS ENUM('member', 'leader');
CREATE TYPE action_type AS ENUM('protest', 'support');
CREATE TYPE vote_type AS ENUM('upvote', 'downvote');

CREATE OR REPLACE FUNCTION unique_ids(numeric) RETURNS boolean AS
$$

	BEGIN
	RETURN NOT EXISTS((SELECT id FROM member WHERE id=$1) UNION 
	(SELECT id FROM action WHERE id=$1) UNION
	(SELECT id FROM project WHERE id=$1 OR authority_id=$1));
	END
$$ 
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION unique_id_wrapper() RETURNS TRIGGER AS
$$
BEGIN
	IF unique_ids(NEW.id) THEN 
		RETURN NEW;
	END IF;
	RETURN NULL;
END	
$$
LANGUAGE plpgsql;

CREATE TABLE member (
	id numeric PRIMARY KEY, -- CHECK(unique_ids(id)),
	password text,
	role_group role_type DEFAULT 'member', -- changing only to member leader and always checking last activity
	last_activity timestamp without time zone,
	upvotes numeric DEFAULT 0, -- adding sum_upvotes/ sum_downvotes for fast trolls checking with trigger on updating actions
	downvotes numeric DEFAULT 0
);
-- ON EVERY INSERT make unique_ids(id)

CREATE TABLE project (
	id numeric PRIMARY KEY, -- CHECK(unique_ids(id)),
	authority_id numeric --REFERENCES authority(id)
);

CREATE TABLE action (
	id numeric PRIMARY KEY, -- CHECK(unique_ids(id)),
	project_id numeric REFERENCES project(id),
	member_id numeric REFERENCES member(id) NOT NULL,
	action action_type NOT NULL,
	upvotes bigint DEFAULT 0,
    downvotes bigint DEFAULT 0	
);

CREATE OR REPLACE FUNCTION check_if_action_exists(numeric) RETURNS BOOLEAN AS
$$
	BEGIN
	RETURN EXISTS(SELECT * FROM action a WHERE a.id=$1);
	END
$$ LANGUAGE plpgsql;

CREATE TABLE member_votes_for_action (
	member_id numeric REFERENCES member(id),
	action_id numeric REFERENCES action(id) CHECK(NOT check_if_action_exists(action_id)),
	vote vote_type NOT NULL,
	PRIMARY KEY (member_id, action_id)
);


CREATE OR REPLACE FUNCTION vote() RETURNS TRIGGER AS 
$$
DECLARE
	troll_id numeric;
BEGIN
	SELECT member_id INTO troll_id FROM action WHERE id = NEW.action_id;
	IF NEW.vote='upvote' THEN
		UPDATE action SET upvotes = upvotes + 1 WHERE id = NEW.action_id;
		UPDATE member SET received_upvotes = received_upvotes + 1 WHERE id = troll_id;
	ELSE
		UPDATE action SET downvotes = downvotes + 1 WHERE id = NEW.action_id;
		UPDATE member SET received_downvotes = received_downvotes + 1 WHERE id = troll_id;
	END IF;
	RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_vote AFTER INSERT ON member_votes_for_action FOR EACH ROW EXECUTE PROCEDURE vote();

CREATE TRIGGER unique_insert_on_member AFTER INSERT ON member FOR EACH ROW EXECUTE PROCEDURE unique_id_wrapper();
CREATE TRIGGER unique_insert_on_action AFTER INSERT ON action FOR EACH ROW EXECUTE PROCEDURE unique_id_wrapper();
CREATE TRIGGER unique_insert_on_project AFTER INSERT ON project FOR EACH ROW EXECUTE PROCEDURE unique_id_wrapper();


COMMIT;

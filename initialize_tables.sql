BEGIN TRANSACTION;

CREATE TYPE role_type AS ENUM('member', 'leader');
CREATE TYPE action_type AS ENUM('protest', 'support');
CREATE TYPE vote_type AS ENUM('upvote', 'downvote');

CREATE OR REPLACE FUNCTION is_id_unique(integer) RETURNS boolean AS
$$

	BEGIN
	RETURN NOT EXISTS((SELECT id FROM member WHERE id=$1) UNION 
	(SELECT id FROM action WHERE id=$1) UNION
	(SELECT id FROM project WHERE id=$1 OR authority_id=$1));
	END
$$ 
LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION unique_id_wrapper() RETURNS TRIGGER AS
$$
BEGIN
	IF NOT is_id_unique(NEW.id) THEN 
		RAISE 'New id is not unique';
	END IF;
	RETURN NEW;
END	
$$
LANGUAGE plpgsql SECURITY DEFINER;

CREATE TABLE member (
	id integer PRIMARY KEY, 
	password text,
	role_group role_type DEFAULT 'member',
	last_activity timestamp without time zone,
	upvotes bigint DEFAULT 0, -- adding sum_upvotes/ sum_downvotes for fast trolls checking with trigger on updating actions
	downvotes bigint DEFAULT 0
);

CREATE TABLE project (
	id integer PRIMARY KEY,
	authority_id integer
);

CREATE TABLE action (
	id integer PRIMARY KEY,
	project_id integer REFERENCES project(id) NOT NULL,
	member_id integer REFERENCES member(id) NOT NULL,
	action action_type NOT NULL,
	upvotes bigint DEFAULT 0,
    downvotes bigint DEFAULT 0	
);

CREATE OR REPLACE FUNCTION action_exist(integer) RETURNS BOOLEAN AS
$$
	BEGIN
	RETURN EXISTS(SELECT * FROM action a WHERE a.id=$1);
	END
$$ LANGUAGE plpgsql;

CREATE TABLE member_votes_for_action (
	member_id integer REFERENCES member(id),
	action_id integer REFERENCES action(id) CHECK(action_exist(action_id)),
	vote vote_type NOT NULL,
	PRIMARY KEY (member_id, action_id)
);


CREATE OR REPLACE FUNCTION vote() RETURNS TRIGGER AS 
$$
DECLARE
	troll_id integer;
BEGIN
	SELECT member_id INTO troll_id FROM action WHERE id = NEW.action_id;
	IF NEW.vote='upvote' THEN
		UPDATE action SET upvotes = upvotes + 1 WHERE id = NEW.action_id;
		UPDATE member SET upvotes = upvotes + 1 WHERE id = troll_id;
	ELSE
		UPDATE action SET downvotes = downvotes + 1 WHERE id = NEW.action_id;
		UPDATE member SET downvotes = downvotes + 1 WHERE id = troll_id;
	END IF;
	RETURN NEW;
END
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_vote AFTER INSERT ON member_votes_for_action FOR EACH ROW EXECUTE PROCEDURE vote();

CREATE TRIGGER unique_insert_on_member BEFORE INSERT ON member FOR EACH ROW EXECUTE PROCEDURE unique_id_wrapper();
CREATE TRIGGER unique_insert_on_action BEFORE INSERT ON action FOR EACH ROW EXECUTE PROCEDURE unique_id_wrapper();
CREATE TRIGGER unique_insert_on_project BEFORE INSERT ON project FOR EACH ROW EXECUTE PROCEDURE unique_id_wrapper();

CREATE OR REPLACE FUNCTION check_project_id(projectid integer, authorityid integer) RETURNS integer AS
$$
BEGIN
	IF NOT EXISTS(select * from project where id=projectid) THEN
		IF authorityid IS NOT NULL THEN
			INSERT INTO project VALUES(projectid, authorityid);
			RETURN projectid;
		ELSE
			RETURN NULL;
		END IF;
	ELSE
		RETURN projectid;
	END IF;
END
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMIT;

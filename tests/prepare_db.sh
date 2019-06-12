echo 'DROP DATABASE student; DROP USER app; CREATE DATABASE student; grant all privileges on database student to init; ' | sudo -u postgres psql;
echo 'CREATE EXTENSION pgcrypto;' | sudo -u postgres psql -d student;


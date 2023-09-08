#!/bin/bash
set -e
echo $POSTGRES_USER

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER docker_user WITH PASSWORD 'asdfgh';
	CREATE DATABASE tracker3;
	GRANT ALL PRIVILEGES ON DATABASE tracker3 TO docker_user;
EOSQL
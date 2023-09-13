#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
ALTER SYSTEM SET max_connections = 50;
ALTER SYSTEM SET shared_buffers = '1GB';
ALTER SYSTEM SET effective_cache_size = '4GB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET temp_file_limit = '10GB';
ALTER SYSTEM SET log_min_duration_statement = '200ms';
ALTER SYSTEM SET idle_in_transaction_session_timeout = '10s';
ALTER SYSTEM SET lock_timeout = '1s';
ALTER SYSTEM SET statement_timeout = '60s';

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
ALTER SYSTEM SET shared_preload_libraries = pg_stat_statements;

CREATE USER $DB_USER WITH PASSWORD '$DB_USER_PASS';
GRANT CONNECT ON DATABASE $POSTGRES_DB TO $DB_USER;
GRANT ALL ON SCHEMA public TO $DB_USER;

EOSQL

#ALTER SYSTEM SET pg_stat_statements.track = 'all';
#ALTER SYSTEM SET pg_stat_statements.max = 10000;

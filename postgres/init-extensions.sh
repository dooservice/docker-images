#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname template1 <<-'EOSQL'
    CREATE EXTENSION IF NOT EXISTS unaccent;
    CREATE EXTENSION IF NOT EXISTS vector;
    ALTER FUNCTION unaccent(text) IMMUTABLE;
EOSQL

# PgDog requires md5 auth — replace the PostgreSQL 16+ default (scram-sha-256)
sed -i 's/scram-sha-256/md5/g' "$PGDATA/pg_hba.conf"

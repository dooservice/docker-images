#!/bin/bash
set -e

# All performance tuning (-c flags) is passed via the container command in bootstrap.py
# and is configurable through DOOSERVICE_PG_* environment variables.
# This script only handles things that cannot be set via command-line flags:
#   1. Extensions that must exist in the template database
#   2. pg_hba.conf auth method (requires file edit, not a GUC parameter)

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname template1 <<-'EOSQL'
    CREATE EXTENSION IF NOT EXISTS unaccent;
    CREATE EXTENSION IF NOT EXISTS vector;

    ALTER FUNCTION unaccent(text) IMMUTABLE;
EOSQL

# Use md5 auth so PgDog (which uses md5) can authenticate against PostgreSQL.
# scram-sha-256 is the PostgreSQL 16+ default but PgDog requires md5.
sed -i 's/scram-sha-256/md5/g' "$PGDATA/pg_hba.conf"

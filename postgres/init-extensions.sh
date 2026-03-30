#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname template1 <<-'EOSQL'
    CREATE EXTENSION IF NOT EXISTS unaccent;
    CREATE EXTENSION IF NOT EXISTS vector;

    ALTER FUNCTION unaccent(text) IMMUTABLE;

    -- ── Auth: md5 for PgDog compatibility ──────────────────────
    ALTER SYSTEM SET password_encryption = 'md5';

    -- ── Connections: PgDog pools connections, PG needs fewer ───
    -- PgDog handles 1000+ client connections, PG only sees pooled ones
    ALTER SYSTEM SET max_connections = 100;

    -- ── Memory: tuned for shared PG behind PgDog ──────────────
    ALTER SYSTEM SET shared_buffers = '4GB';
    ALTER SYSTEM SET effective_cache_size = '32GB';
    ALTER SYSTEM SET work_mem = '8MB';
    ALTER SYSTEM SET maintenance_work_mem = '512MB';

    -- ── SSD-optimized I/O ─────────────────────────────────────
    ALTER SYSTEM SET random_page_cost = 1.1;
    ALTER SYSTEM SET effective_io_concurrency = 200;

    -- ── WAL ───────────────────────────────────────────────────
    ALTER SYSTEM SET wal_compression = on;
    ALTER SYSTEM SET checkpoint_completion_target = 0.9;
    ALTER SYSTEM SET max_wal_size = '4GB';
    ALTER SYSTEM SET min_wal_size = '1GB';

    -- ── Autovacuum ────────────────────────────────────────────
    ALTER SYSTEM SET autovacuum_max_workers = 4;
    ALTER SYSTEM SET autovacuum_naptime = '30s';
    ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.05;

    -- ── Connection keepalive (detect dead PgDog connections) ──
    ALTER SYSTEM SET tcp_keepalives_idle = 60;
    ALTER SYSTEM SET tcp_keepalives_interval = 10;
    ALTER SYSTEM SET tcp_keepalives_count = 6;

    -- ── Timeouts ──────────────────────────────────────────────
    ALTER SYSTEM SET idle_in_transaction_session_timeout = '300s';
    ALTER SYSTEM SET idle_session_timeout = '600s';
    ALTER SYSTEM SET statement_timeout = '300s';

    SELECT pg_reload_conf();
EOSQL

# Force md5 auth in pg_hba.conf for PgDog compatibility
sed -i 's/scram-sha-256/md5/g' "$PGDATA/pg_hba.conf"

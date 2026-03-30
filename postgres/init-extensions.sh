#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname template1 <<-'EOSQL'
    CREATE EXTENSION IF NOT EXISTS unaccent;
    CREATE EXTENSION IF NOT EXISTS vector;

    ALTER FUNCTION unaccent(text) IMMUTABLE;

    -- Connection limits (9-15 Odoo instances × ~6 conn each = ~90 active)
    ALTER SYSTEM SET max_connections = 200;

    -- Memory: conservative for shared PG serving many Odoo instances
    -- Server: 64GB RAM, but Odoo containers need ~500MB each
    ALTER SYSTEM SET shared_buffers = '4GB';
    ALTER SYSTEM SET effective_cache_size = '32GB';
    ALTER SYSTEM SET work_mem = '8MB';
    ALTER SYSTEM SET maintenance_work_mem = '512MB';

    -- SSD-optimized I/O
    ALTER SYSTEM SET random_page_cost = 1.1;
    ALTER SYSTEM SET effective_io_concurrency = 200;

    -- WAL
    ALTER SYSTEM SET wal_compression = on;
    ALTER SYSTEM SET checkpoint_completion_target = 0.9;
    ALTER SYSTEM SET max_wal_size = '4GB';
    ALTER SYSTEM SET min_wal_size = '1GB';

    -- Autovacuum: less aggressive to avoid spikes
    ALTER SYSTEM SET autovacuum_max_workers = 4;
    ALTER SYSTEM SET autovacuum_naptime = '30s';
    ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.05;

    -- Connection keepalive (detect dead Odoo workers faster)
    ALTER SYSTEM SET tcp_keepalives_idle = 60;
    ALTER SYSTEM SET tcp_keepalives_interval = 10;
    ALTER SYSTEM SET tcp_keepalives_count = 6;

    -- Statement timeout: kill queries stuck >5min (prevents longpoll stalls)
    ALTER SYSTEM SET idle_in_transaction_session_timeout = '300s';

    SELECT pg_reload_conf();
EOSQL
# PostgreSQL 16 with pgvector, the database every environment of a server shares.
FROM postgres:16@sha256:1beaa3084eee2676f20a9cd9928f0bf2c5bf674f8e49f81017912183d377c61c

RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-"${PG_MAJOR}"-pgvector \
 && rm -rf /var/lib/apt/lists/*

COPY init-extensions.sh /docker-entrypoint-initdb.d/10-extensions.sh

HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 \
    CMD ["/bin/sh", "-c", "pg_isready -U \"$POSTGRES_USER\" || exit 1"]

ARG PG_VERSION=16
FROM postgres:${PG_VERSION}

RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-"${PG_MAJOR}"-pgvector \
 && rm -rf /var/lib/apt/lists/*

COPY init-extensions.sh /docker-entrypoint-initdb.d/10-extensions.sh

HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 \
    CMD pg_isready -U "$POSTGRES_USER" || exit 1

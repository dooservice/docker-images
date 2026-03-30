#!/bin/bash
# Not used — edoburu/pgbouncer handles config via env vars natively.
# Kept for reference of env vars used:
#
#   DB_HOST          - upstream postgres host (default: dooservice-shared-postgres)
#   DB_USER          - superuser name
#   DB_PASSWORD      - superuser password
#   POOL_MODE        - pool mode (default: transaction)
#   MAX_CLIENT_CONN  - max client connections (default: 1000)
#   DEFAULT_POOL_SIZE - connections per user/db pair (default: 20)
#   MIN_POOL_SIZE    - minimum connections kept (default: 5)
#   AUTH_TYPE         - auth type (default: scram-sha-256)

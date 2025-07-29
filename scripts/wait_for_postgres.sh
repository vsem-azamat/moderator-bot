#!/bin/sh
set -e

host=${DB_HOST:-db}

until PGPASSWORD="$DB_PASSWORD" psql -h "$host" -U "$DB_USER" -d "$DB_NAME" -c '\q' >/dev/null 2>&1; do
  echo "Waiting for Postgres at $host..."
  sleep 1
done

exec "$@"

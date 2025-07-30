#!/bin/sh
set -e

host=${DB_HOST:-db}
max_attempts=${POSTGRES_WAIT_ATTEMPTS:-60}
attempts=0

while ! PGPASSWORD="$DB_PASSWORD" psql -h "$host" -U "$DB_USER" -d "$DB_NAME" -c '\q' >/dev/null 2>&1; do
  attempts=$((attempts + 1))
  if [ "$attempts" -ge "$max_attempts" ]; then
    echo "Postgres still not reachable after $attempts attempts, exiting."
    exit 1
  fi
  echo "Waiting for Postgres at $host..."
  sleep 1
done

exit 0

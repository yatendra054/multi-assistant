#!/bin/sh

# Default values if env vars not set
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-3306}

echo "Waiting for database at $DB_HOST:$DB_PORT..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "Database is up!"

echo "Running makemigrations..."
python manage.py makemigrations --noinput

echo "Running migrate..."
python manage.py migrate --noinput

exec "$@"
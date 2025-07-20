#!/bin/sh

# Default values if env vars not set
HOST=${HOST}
PORT=${PORT}

echo "ENV HOST: $HOST"
echo "ENV PORT: $PORT"

echo "Waiting for database at $HOST:$PORT..."
while ! nc -z "$HOST" "$PORT"; do
  sleep 1
done

echo "Database is up!"

echo "Running makemigrations..."
python manage.py makemigrations --noinput

echo "Running migrate..."
python manage.py migrate --noinput

exec "$@"
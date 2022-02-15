#!/bin/sh

echo "Waiting for db..."

while ! nc -z db 3306; do
    sleep 0.1
done

echo "MariaDB started"

/usr/src/app/manage.py collectstatic -c --noinput
/usr/src/app/manage.py migrate

exec "$@"

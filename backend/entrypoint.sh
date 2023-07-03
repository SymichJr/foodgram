#!/bin/sh

while ! nc -z db 5432;
    do sleep .5;
    echo "wait db";
done;
    echo "connected to the db";

python manage.py migrate;
python manage.py collectstatic --noinput;
gunicorn -w 2 -b 0:8000 foodgram.wsgi;
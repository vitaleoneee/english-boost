#!/bin/sh

if [ "$POSTGRES_DB" = "english-boost" ]
then
    echo "Wait postgres..."

    while ! nc -z "db" "$POSTGRES_PORT"; do
      sleep 0.5
    done

    echo "PostgreSQL is ready!"
fi

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py loaddata ./fixtures.json

echo "
from django.contrib.auth import get_user_model
User = get_user_model()

username='${DJANGO_SUPERUSER_USERNAME}'
email='${DJANGO_SUPERUSER_EMAIL}'
password='${DJANGO_SUPERUSER_PASSWORD}'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created:', username)
else:
    print('Superuser already exists:', username)
" | python manage.py shell

exec "$@"
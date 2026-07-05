#!/bin/sh

# Dev startup script for local development only.

set -e

# create the local media directory
mkdir -p /app/library/user-media
chown -R 10001:10001 /app/library/user-media

# ensure a dev superuser exists
python manage.py shell -c '
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()
user, created = User.objects.get_or_create(
    username="conrad",
    defaults={
        "email": "conrad@example.com",
        "is_staff": True,
        "is_superuser": True,
    },
)
user.is_staff = True
user.is_superuser = True
user.password = make_password("password")
user.save()
'

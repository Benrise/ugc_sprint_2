import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("ADMIN_DJANGO_DB_NAME"),
        "USER": os.environ.get("ADMIN_DJANGO_DB_USER"),
        "PASSWORD": os.environ.get("ADMIN_DJANGO_DB_PASSWORD"),
        "HOST": os.environ.get("ADMIN_DJANGO_DB_HOST"),
        "PORT": os.environ.get("ADMIN_DJANGO_DB_PORT"),
        "OPTIONS": {"options": "-c search_path=content,public"},
    }
}

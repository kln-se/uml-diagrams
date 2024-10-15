import environ
from django.db import migrations
from rest_framework.authtoken.models import Token
from pathlib import Path

from apps.users.models import User


class CreateSuperuser:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
    superuser: User

    @classmethod
    def get_env(cls):
        env = environ.Env()
        if env.bool("DJANGO_READ_ENV_FILE", default=True):
            env.read_env(str(cls.BASE_DIR / ".env"))
        return env

    @classmethod
    def generate_token(cls, *_args):
        Token.objects.create(user=cls.superuser)

    @classmethod
    def create_superuser(cls, *_args):
        env = cls.get_env()
        superuser = User.objects.filter(
            email=env.str("SUPERUSER_EMAIL"))
        if not superuser.exists():
            cls.superuser = User.objects.create_superuser(
                email=env.str("SUPERUSER_EMAIL"),
                password=env.str("SUPERUSER_PASSWORD"),
            )
            cls.superuser.save()
            cls.generate_token()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(CreateSuperuser.create_superuser),
    ]

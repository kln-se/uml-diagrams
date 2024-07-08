from django.db import migrations
from rest_framework.authtoken.models import Token

from apps.users.models import User

SUPERUSER_EMAIL = 'admin@example.org'
SUPERUSER_PASSWORD = 'admin'


class CreateSuperuser:
    superuser: User

    @classmethod
    def create_superuser(cls, apps, schema_editor):
        cls.superuser = User.objects.create_superuser(
            email=SUPERUSER_EMAIL,
            password=SUPERUSER_PASSWORD,
        )
        cls.superuser.save()

    @classmethod
    def generate_token(cls, apps, schema_editor):
        Token.objects.create(user=cls.superuser)


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(CreateSuperuser.create_superuser),
        migrations.RunPython(CreateSuperuser.generate_token),
    ]

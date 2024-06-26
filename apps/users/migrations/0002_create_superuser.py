from django.db import migrations
from apps.users.models import User


def create_superuser(apps, schema_editor):
    superuser = User.objects.create_superuser(
        email='admin@example.org',
        password='admin',
        first_name='admin',
        last_name='admin',
        is_staff=True,
        is_active=True
    )
    superuser.save()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]

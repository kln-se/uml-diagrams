from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.users.managers import UserManager


class User(AbstractUser):
    email: str = models.EmailField(unique=True)
    # Set email field to be unique user's identifier instead of username field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # Disabled Django's default fields
    username = None
    groups = None
    user_permissions = None

    # Custom fields
    # ...

    objects = UserManager()

    def __str__(self):
        return f"User: {self.email}"

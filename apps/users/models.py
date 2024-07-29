import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.constants import UserRoles
from apps.users.managers import UserManager


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=32, choices=UserRoles.CHOICES, default=UserRoles.USER
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # Disabled Django's default fields
    username = None
    groups = None
    user_permissions = None

    objects = UserManager()

    @property
    def is_user(self):
        return self.role == UserRoles.USER

    @property
    def is_moderator(self):
        return self.role in (UserRoles.MODERATOR, UserRoles.ADMIN)

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.role}: {self.email}"

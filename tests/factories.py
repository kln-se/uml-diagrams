import factory
from factory.django import DjangoModelFactory

from apps.diagrams.models import Diagram
from apps.users.constants import PASSWORD_MIN_LENGTH, UserRoles
from apps.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    password = factory.Faker(
        "password",
        length=PASSWORD_MIN_LENGTH,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = factory.Iterator(UserRoles.CHOICES, getter=lambda x: x[0])


class DiagramFactory(DjangoModelFactory):
    class Meta:
        model = Diagram

    title = factory.Faker("sentence")
    json = factory.Faker("json")
    description = factory.Faker("text")
    owner = factory.SubFactory(UserFactory)
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")

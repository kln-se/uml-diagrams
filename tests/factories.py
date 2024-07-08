import factory
from factory.django import DjangoModelFactory

from apps.diagrams.models import Diagram
from apps.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    password = factory.Faker("password")


class DiagramFactory(DjangoModelFactory):
    class Meta:
        model = Diagram

    title = factory.Faker("sentence")
    json = factory.Faker("json")
    description = factory.Faker("text")
    owner = factory.SubFactory(UserFactory)
    created_at = factory.Faker("date_time")
    updated_at = factory.Faker("date_time")

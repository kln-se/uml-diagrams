import factory
from factory.django import DjangoModelFactory
from faker import Faker

from apps.diagrams.models import Diagram
from apps.sharings.constants import PermissionLevels
from apps.sharings.models import Collaborator
from apps.users.constants import PASSWORD_MIN_LENGTH, UserRoles
from apps.users.models import User


class FakePassword:
    faker_obj = Faker()
    default_password_options = {
        "length": PASSWORD_MIN_LENGTH,
        "special_chars": True,
        "digits": True,
        "upper_case": True,
        "lower_case": True,
    }

    @classmethod
    def generate(cls, **kwargs) -> str:
        """Generate a random password according to the given options."""
        if kwargs:
            password_options = cls.default_password_options.copy()
            password_options.update(kwargs)
            return cls.faker_obj.password(**password_options)
        return cls.faker_obj.password(**cls.default_password_options)


DEFAULT_TEST_PASSWORD = FakePassword.generate()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    password = factory.django.Password(password=DEFAULT_TEST_PASSWORD)
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


class CollaboratorFactory(DjangoModelFactory):
    class Meta:
        model = Collaborator

    diagram = factory.SubFactory(DiagramFactory)
    shared_to = factory.SubFactory(UserFactory)
    permission_level = factory.Iterator(PermissionLevels.CHOICES, getter=lambda x: x[0])

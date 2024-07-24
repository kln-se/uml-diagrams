import factory
from factory.django import DjangoModelFactory
from faker import Faker

from apps.diagrams.models import Diagram
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


class UserFactory(DjangoModelFactory):

    @staticmethod
    def inject_random_generated_password(super_method, **kwargs):
        """Inject a random generated password into the kwargs
        if password was not provided. And add raw password value
        to the user object.
        """
        password = kwargs.get("password")
        if password is None:
            password = FakePassword.generate()
            kwargs["password"] = password
        user = super_method(**kwargs)
        user._raw_password = password
        return user

    @classmethod
    def build(cls, **kwargs):
        """Override build() method to generate and save the raw password value."""
        return cls.inject_random_generated_password(super().build, **kwargs)

    @classmethod
    def create(cls, **kwargs):
        """Override create() method to generate and save the raw password value."""
        return cls.inject_random_generated_password(super().create, **kwargs)

    class Meta:
        model = User

    email = factory.Faker("email")
    password = factory.django.Password(password=None)
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

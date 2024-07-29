import pytest
from faker import Faker

from apps.users.api.v1.serializers import SignupUserSerializer, UserSerializer
from apps.users.constants import PASSWORD_MIN_LENGTH, UserRoles
from apps.users.models import User
from tests.factories import FakePassword, UserFactory


@pytest.fixture
def user() -> User:
    return UserFactory()


class TestUserSerializer:
    def test_user_serializer_correct_returned_data(self, user: User) -> None:
        """
        GIVEN a random user
        WHEN serializer is called
        THEN check if serialized data is coincident with the user's data.
        """
        serializer = UserSerializer(user)
        assert serializer.data == {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }

    def test_user_serializer_update_password(self, user: User) -> None:
        """
        GIVEN a random user trying to update password
        WHEN serializer is called with new password
        THEN check that password is changed.
        """
        new_password = FakePassword.generate()
        serializer = UserSerializer(user, data={"password": new_password}, partial=True)
        assert serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        assert instance.check_password(new_password)

    def test_user_serializer_email_unique_validator(self, user: User) -> None:
        """
        GIVEN a random user trying to use a non-unique email
        WHEN serializer is called with a used email
        THEN check that email is not changed.
        """
        another_user = UserFactory()
        serializer = UserSerializer(
            user, data={"email": another_user.email}, partial=True
        )
        assert not serializer.is_valid()
        assert "email" in serializer.errors


class TestSignupUserSerializer:
    def test_signup_user_serializer_correct_returned_data(self, user: User) -> None:
        """
        GIVEN a random user
        WHEN serializer is called
        THEN check if serialized data is coincident with the user's data.
        """
        serializer = SignupUserSerializer(user)
        assert serializer.data == {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }

    def test_signup_user_serializer_input_data(self) -> None:
        """
        GIVEN a random user trying to signup with valid data
        WHEN serializer is called
        THEN check that data serialized to user object correctly.
        """
        raw_password = FakePassword.generate()
        fake_user_data = UserFactory.build(password=raw_password)
        signup_data = {
            "email": fake_user_data.email,
            "password": raw_password,
            "first_name": fake_user_data.first_name,
            "last_name": fake_user_data.last_name,
        }
        serializer = SignupUserSerializer(data=signup_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(validated_data=serializer.validated_data)
        assert instance.email == signup_data["email"]
        assert instance.check_password(signup_data["password"])
        assert instance.first_name == signup_data["first_name"]
        assert instance.last_name == signup_data["last_name"]

    @pytest.mark.parametrize(
        ("password", "code"),
        [
            (
                FakePassword.generate(length=PASSWORD_MIN_LENGTH - 1),
                "password_too_short",
            ),
            (
                FakePassword.generate(special_chars=False),
                "password_missing_special_chars",
            ),
            (FakePassword.generate(upper_case=False), "password_missing_uppercase"),
            (FakePassword.generate(lower_case=False), "password_missing_lowercase"),
            (FakePassword.generate(digits=False), "password_missing_digit"),
        ],
    )
    def test_signup_user_serializer_enabled_password_validators(
        self, password: str, code: str
    ) -> None:
        """
        GIVEN a random user trying to signup with invalid password
        WHEN serializer is called
        THEN check that password is not meet the requirements.
        """
        signup_data = {"email": Faker().email(), "password": password}
        serializer = SignupUserSerializer(data=signup_data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors
        assert serializer.errors["password"][0].code == code

    def test_signup_user_serializer_read_only_fields_in_input_data(self) -> None:
        """
        GIVEN a random user, who set `id` and `role` fields in request body
        WHEN serializer is called
        THEN check if through validation `role` was set to `user` and `id` is different.
        """
        raw_password = FakePassword.generate()
        fake_user_data = UserFactory.build(role=UserRoles.ADMIN, password=raw_password)
        signup_data = {
            "id": Faker().uuid4(),
            "email": fake_user_data.email,
            "password": raw_password,
            "role": UserRoles.ADMIN,
        }
        serializer = SignupUserSerializer(data=signup_data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(validated_data=serializer.validated_data)
        assert instance.pk != signup_data["id"]
        assert instance.role == UserRoles.USER

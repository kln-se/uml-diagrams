import pytest
from faker import Faker

from apps.users.api.v1.serializers import SignupUserSerializer, UserSerializer
from apps.users.constants import PASSWORD_MIN_LENGTH, UserRoles
from apps.users.models import User
from tests.factories import UserFactory


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
        new_password = Faker().password(
            length=PASSWORD_MIN_LENGTH,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )
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

    def test_signup_user_serializer_input_data(self, user: User) -> None:
        """
        GIVEN a random user trying to signup with valid data
        WHEN serializer is called
        THEN check that data serialized to user object correctly.
        """
        user.delete()  # factory adds user to db, so we need to delete it before test
        serializer = SignupUserSerializer(  # user used just for fake data
            data={
                "email": user.email,
                "password": user.password,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(validated_data=serializer.validated_data)
        assert instance.email == user.email
        assert instance.check_password(user.password)
        assert instance.first_name == user.first_name
        assert instance.last_name == user.last_name

    @pytest.mark.parametrize(
        ("password", "code"),
        [
            ("123aA.", "password_too_short"),
            ("12345678aA", "password_missing_special_chars"),
            ("12345678a.", "password_missing_uppercase"),
            ("12345678A.", "password_missing_lowercase"),
            ("aaaaaaaaA.", "password_missing_digit"),
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
        serializer = SignupUserSerializer(
            data={
                "email": Faker().email(),
                "password": password,
            }
        )
        assert not serializer.is_valid()
        assert "password" in serializer.errors
        assert serializer.errors["password"][0].code == code

    def test_signup_user_serializer_read_only_fields_in_input_data(self) -> None:
        """
        GIVEN a random user, who set `id` and `role` fields in request body
        WHEN serializer is called
        THEN check if through validation `role` was set to `user` and `id` is different.
        """
        faker_obj = Faker()
        user_id = faker_obj.pyint()
        serializer = SignupUserSerializer(
            data={
                "id": user_id,
                "email": faker_obj.email(),
                "password": faker_obj.password(),
                "role": UserRoles.ADMIN,
            }
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(validated_data=serializer.validated_data)
        assert instance.pk != user_id
        assert instance.role == UserRoles.USER

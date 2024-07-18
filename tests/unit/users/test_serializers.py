import pytest
from faker import Faker

from apps.users.api.v1.serializers import SignupUserSerializer, UserSerializer
from apps.users.constants import UserRoles
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
        new_password = Faker().password()
        serializer = UserSerializer(user, data={"password": new_password}, partial=True)
        assert serializer.is_valid()
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

    @pytest.mark.xfail(reason="Due to password validation")
    def test_signup_user_serializer_input_data(self, user: User) -> None:
        """
        GIVEN a random user trying to signup
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

    def test_signup_user_serializer_read_only_fields_in_input_data(self) -> None:
        """
        GIVEN a random user, who set `id` and `role` fields in request body
        WHEN serializer is called
        THEN check if through validation `role` was set to `user` and `id` is different.
        """
        user_id = Faker().pyint()
        serializer = SignupUserSerializer(
            data={
                "id": user_id,
                "email": Faker().email(),
                "password": Faker().password(),
                "role": UserRoles.ADMIN,
            }
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(validated_data=serializer.validated_data)
        assert instance.pk != user_id
        assert instance.role == UserRoles.USER

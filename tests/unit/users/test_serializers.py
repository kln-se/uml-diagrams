from apps.users.api.v1.serializers import SignupUserSerializer, UserSerializer
from apps.users.constants import UserRoles
from tests.factories import UserFactory


class TestUserSerializer:
    def test_user_serializer_data(self):
        """
        GIVEN a random user
        WHEN serializer is called
        THEN check if serialized data is coincident with the user's data.
        """
        user = UserFactory()
        serializer = UserSerializer(user)
        assert serializer.data == {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }


class TestSignupUserSerializer:
    def test_signup_user_serializer_data(self):
        """
        GIVEN a random user
        WHEN serializer is called
        THEN check if serialized data is coincident with the user's data.
        """
        user = UserFactory()
        serializer = SignupUserSerializer(user)
        assert serializer.data == {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }

    def test_user_trying_to_signup_as_admin_serializer_data(self):
        """
        GIVEN a random user, who set `admin` to the role field in request body
        WHEN serializer is called
        THEN check if through validation it was set to `user`.
        """
        user = UserFactory()  # Using factory just to generate user date
        user.delete()  # Factory adds user to db, so we need to delete it before test
        serializer = SignupUserSerializer(
            data={
                "id": user.id,
                "email": user.email,
                "password": user.password,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": UserRoles.ADMIN,
            }
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.create(validated_data=serializer.validated_data)
        assert instance.role == UserRoles.USER

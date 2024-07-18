from apps.authentication.api.v1.serializers import CustomAuthTokenSerializer
from tests.factories import UserFactory


def test_custom_auth_token_serializer_email_required_in_input() -> None:
    """
    GIVEN a login data, username used instead of email
    WHEN serializer is called
    THEN check that email field is required
    """
    user = UserFactory()
    serializer = CustomAuthTokenSerializer(
        data={"username": user.email, "password": user.password}
    )
    assert not serializer.is_valid()
    assert "email" in serializer.errors
    assert serializer.errors["email"][0].code == "required"


def test_custom_auth_token_serializer_no_write_only_fields_in_returned_data() -> None:
    """
    GIVEN user object
    WHEN serializer is called
    THEN check that email field is not returned
    """
    user = UserFactory()
    serializer = CustomAuthTokenSerializer(user)
    assert "email" not in serializer.data

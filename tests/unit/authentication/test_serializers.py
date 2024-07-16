from apps.authentication.api.v1.serializers import CustomAuthTokenSerializer
from tests.factories import UserFactory


def test_custom_auth_token_serializer_email_required():
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

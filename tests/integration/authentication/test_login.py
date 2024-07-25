import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from tests.factories import UserFactory
from tests.integration.authentication.constants import LOGIN_URL


def test_login_with_valid_credentials(client: APIClient) -> None:
    """
    GIVEN valid user credentials
    WHEN POST api/v1/login is requested
    THEN check that user is authenticated.
    """
    user = UserFactory()
    user_credentials = {
        "email": user.email,
        "password": user._raw_password,
    }
    response = client.post(path=LOGIN_URL, data=user_credentials)
    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.json()
    token = Token.objects.filter(key=response.data["token"]).first()
    assert token is not None
    assert token.user == user


def test_login_user_not_found(client: APIClient) -> None:
    """
    GIVEN invalid user credentials
    WHEN POST api/v1/login is requested
    THEN check that user is not authenticated.
    """
    fake_user_data = UserFactory.build()
    user_credentials = {
        "email": fake_user_data.email,
        "password": fake_user_data._raw_password,
    }
    response = client.post(path=LOGIN_URL, data=user_credentials)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "non_field_errors": ["Unable to log in with provided credentials."]
    }


def test_login_invalid_password(client: APIClient) -> None:
    """
    GIVEN invalid user password
    WHEN POST api/v1/login is requested
    THEN check that user is not authenticated.
    """
    user = UserFactory()
    user_credentials = {
        "email": user.email,
        "password": "invalid_password",
    }
    response = client.post(path=LOGIN_URL, data=user_credentials)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "non_field_errors": ["Unable to log in with provided credentials."]
    }


@pytest.mark.parametrize(
    "method",
    (
        "get",
        "put",
        "patch",
        "delete",
    ),
)
def test_login_allowed_http_methods(client: APIClient, method: str) -> None:
    """
    GIVEN valid user credentials
    WHEN other than POST method for /api/v1/login/ is requested
    THEN check that it returns 405 METHOD NOT ALLOWED
    """
    user = UserFactory()
    user_credentials = {"email": user.email, "password": user._raw_password}
    response = getattr(client, method)(path=LOGIN_URL, data=user_credentials)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

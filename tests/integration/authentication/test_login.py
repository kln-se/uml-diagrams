import pytest
from faker import Faker
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
    faker_obj = Faker()
    user_credentials = {"email": faker_obj.email(), "password": faker_obj.password()}
    user = UserFactory(**user_credentials)
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
    faker_obj = Faker()
    user_credentials = {"email": faker_obj.email(), "password": faker_obj.password()}
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
    response = client.post(
        path=LOGIN_URL,
        data={
            "email": user.email,
            "password": "invalid_password",
        },
    )
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
    faker_obj = Faker()
    user_credentials = {"email": faker_obj.email(), "password": faker_obj.password()}
    _ = UserFactory(**user_credentials)
    response = getattr(client, method)(
        path=LOGIN_URL,
        data=user_credentials,
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

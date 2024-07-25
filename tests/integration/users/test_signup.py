import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.constants import UserRoles
from apps.users.models import User
from tests.factories import FakePassword, UserFactory
from tests.integration.users.constants import SIGNUP_URL


def test_signup_user_with_valid_data(client: APIClient) -> None:
    """
    GIVEN valid signup user data
    WHEN POST /api/v1/signup/ is requested
    THEN check that user is created with valid data
    """
    raw_password = FakePassword.generate()
    fake_user_data = UserFactory.build(password=raw_password)
    signup_data = {
        "email": fake_user_data.email,
        "password": raw_password,
        "first_name": fake_user_data.first_name,
        "last_name": fake_user_data.last_name,
    }
    response = client.post(
        path=SIGNUP_URL,
        data=signup_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email=response.data["email"]).exists()
    user = User.objects.get(email=response.data["email"])
    user.check_password(signup_data["password"])
    assert user.id == response.data["id"]
    assert user.email == response.data["email"] == signup_data["email"]
    assert user.first_name == response.data["first_name"] == signup_data["first_name"]
    assert user.last_name == response.data["last_name"] == signup_data["last_name"]


def test_signup_user_valid_role_granted(client: APIClient) -> None:
    """
    GIVEN signup user data with invalid role
    WHEN POST /api/v1/signup/ is requested
    THEN check that user is created with valid role `user`
    """
    raw_password = FakePassword.generate()
    fake_user_data = UserFactory.build(password=raw_password)
    signup_data = {
        "email": fake_user_data.email,
        "password": raw_password,
        "role": UserRoles.ADMIN,
    }
    response = client.post(
        path=SIGNUP_URL,
        data=signup_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(email=response.data["email"])
    assert user.role == UserRoles.USER


def test_signup_user_email_already_exists(client: APIClient) -> None:
    """
    GIVEN valid signup user data but email already exists
    WHEN POST /api/v1/signup/ is requested
    THEN check that user is not created
    """
    registered_user = UserFactory()
    signup_data = {
        "email": registered_user.email,
        "password": FakePassword.generate(),
    }
    response = client.post(
        path=SIGNUP_URL,
        data=signup_data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["email"][0].code == "unique"
    assert User.objects.filter(email=registered_user.email).count() == 1


@pytest.mark.parametrize(
    "method",
    (
        "get",
        "put",
        "patch",
        "delete",
    ),
)
def test_signup_user_allowed_http_methods(client: APIClient, method: str) -> None:
    """
    GIVEN valid signup user data
    WHEN other than POST method for /api/v1/signup/ is requested
    THEN check that it returns 405 METHOD NOT ALLOWED
    """
    raw_password = FakePassword.generate()
    fake_user_data = UserFactory.build(password=raw_password)
    signup_data = {
        "email": fake_user_data.email,
        "password": raw_password,
    }
    response = getattr(client, method)(
        path=SIGNUP_URL,
        data=signup_data,
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

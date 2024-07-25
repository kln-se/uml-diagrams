import pytest
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.constants import UserRoles
from apps.users.models import User
from tests.factories import FakePassword, UserFactory
from tests.integration.users.constants import USER_DETAIL_URL


@pytest.mark.parametrize(
    "method",
    [
        "get",
        "put",
        "patch",
    ],
)
def test_retrieve_update_me_requires_authentication(
    client: APIClient, method: str
) -> None:
    response = getattr(client, method)(
        path=USER_DETAIL_URL,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["detail"].code == "not_authenticated"


@pytest.mark.parametrize(
    ("method", "status_code"),
    [
        ("get", status.HTTP_200_OK),
        ("put", status.HTTP_200_OK),
        ("patch", status.HTTP_200_OK),
        ("post", status.HTTP_405_METHOD_NOT_ALLOWED),
        ("delete", status.HTTP_405_METHOD_NOT_ALLOWED),
    ],
)
def test_retrieve_update_me_allowed_http_methods(
    client: APIClient, logged_in_user: User, method: str, status_code: int
) -> None:
    response = getattr(client, method)(
        path=USER_DETAIL_URL,
    )
    assert response.status_code == status_code


def test_retrieve_logged_in_me(client: APIClient, logged_in_user: User) -> None:
    """
    GIVEN a logged-in user
    WHEN GET /api/v1/users/me/ is requested
    THEN check that he receives 200 OK and his account data
    """
    response = client.get(
        path=USER_DETAIL_URL,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == logged_in_user.pk
    assert response.data["email"] == logged_in_user.email
    assert response.data["first_name"] == logged_in_user.first_name
    assert response.data["last_name"] == logged_in_user.last_name
    assert response.data["role"] == logged_in_user.role


def test_update_myself_user_info(client: APIClient, logged_in_user: User) -> None:
    """
    GIVEN a logged-in user
    WHEN PUT /api/v1/users/me/ is requested
    THEN check that he receives 200 OK and his account data was updated
    """
    raw_password = FakePassword.generate()
    fake_user_data = UserFactory.build(password=raw_password)
    data_to_update = {
        "email": fake_user_data.email,
        "password": raw_password,
        "first_name": fake_user_data.first_name,
        "last_name": fake_user_data.last_name,
    }
    response = client.put(path=USER_DETAIL_URL, data=data_to_update)
    assert response.status_code == status.HTTP_200_OK
    user = User.objects.get(pk=logged_in_user.pk)
    assert user.id == response.data["id"] == logged_in_user.pk
    assert user.email == response.data["email"] == data_to_update["email"]
    assert user.check_password(data_to_update["password"])
    assert (
        user.first_name == response.data["first_name"] == data_to_update["first_name"]
    )
    assert user.last_name == response.data["last_name"] == data_to_update["last_name"]


@pytest.mark.parametrize(
    ("field_name", "field_value", "expected"),
    [
        ("id", Faker().pyint(), False),
        ("email", Faker().email(), True),
        ("password", FakePassword.generate(), True),
        ("first_name", Faker().first_name(), True),
        ("last_name", Faker().last_name(), True),
        ("role", UserRoles.ADMIN, False),
    ],
)
def test_partial_update_myself_user_info(
    client: APIClient,
    logged_in_user: User,
    field_name: str,
    field_value: str,
    expected: bool,
) -> None:
    """
    GIVEN a logged-in user
    WHEN PATCH /api/v1/users/me/ is requested
    THEN check that he receives 200 OK and his account data was updated
    """
    data_to_update = {field_name: field_value}
    response = client.patch(path=USER_DETAIL_URL, data=data_to_update)
    assert response.status_code == status.HTTP_200_OK
    user = User.objects.get(pk=logged_in_user.pk)
    if field_name == "password":
        assert user.check_password(data_to_update[field_name])
    else:
        assert (getattr(user, field_name) == data_to_update[field_name]) == expected


def test_partial_update_myself_user_info_email_already_exists(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN a logged-in user trying to update his email with existing one
    WHEN PATCH /api/v1/users/me/ is requested
    THEN check that he receives 400 BAD REQUEST
    """
    registered_user = UserFactory()
    data_to_update = {"email": registered_user.email}
    response = client.patch(path=USER_DETAIL_URL, data=data_to_update)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["email"][0].code == "unique"
    assert User.objects.filter(email=registered_user.email).count() == 1

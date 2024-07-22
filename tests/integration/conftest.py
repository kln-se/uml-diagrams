import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.users.constants import UserRoles
from tests.factories import UserFactory


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def logged_in_user(client: APIClient):
    user = UserFactory(role=UserRoles.USER)
    token = Token.objects.create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return user


@pytest.fixture
def logged_in_admin(client: APIClient):
    admin = UserFactory(role=UserRoles.ADMIN)
    token = Token.objects.create(user=admin)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return admin

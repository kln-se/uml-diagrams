import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.users.models import User
from tests.integration.authentication.constants import LOGOUT_URL


def test_logout_token_is_deleted_successfully(
    client: APIClient, logged_in_user: User
) -> None:
    """
    GIVEN logged-in user who wants to log out
    WHEN POST api/v1/logout is requested
    THEN check that user
    """
    response = client.post(path=LOGOUT_URL)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(User.auth_token.RelatedObjectDoesNotExist) as ex:
        _ = User.objects.get(email=logged_in_user.email).auth_token
    assert ex.value.args[0] == "User has no auth_token."
    assert not Token.objects.filter(user=logged_in_user).exists()


def test_logout_not_authenticated_user(client: APIClient) -> None:
    """
    GIVEN not logged-in user who tries to log out
    WHEN POST api/v1/logout is requested
    THEN check that 401 UNAUTHORIZED is returned
    """
    response = client.post(path=LOGOUT_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Authentication credentials were not provided."
    }
    assert response.data["detail"].code == "not_authenticated"


@pytest.mark.parametrize(
    "method",
    (
        "get",
        "put",
        "patch",
        "delete",
    ),
)
def test_login_allowed_http_methods(
    client: APIClient, logged_in_user: User, method: str
) -> None:
    """
    GIVEN a logged-in user who wants to log out
    WHEN other than POST method for /api/v1/login/ is requested
    THEN check that it returns 405 METHOD NOT ALLOWED
    """
    response = getattr(client, method)(path=LOGOUT_URL)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

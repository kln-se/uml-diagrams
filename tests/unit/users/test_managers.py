import pytest

from apps.users.constants import UserRoles
from apps.users.models import User
from tests.factories import FakePassword, UserFactory


@pytest.fixture
def user_data() -> User:
    return UserFactory.build()


@pytest.fixture
def raw_password() -> str:
    return FakePassword.generate()


class TestSuperuserManager:
    def test_create_superuser_superuser_access_granted(
        self, user_data: User, raw_password: str
    ) -> None:
        user = User.objects.create_superuser(
            email=user_data.email, password=raw_password
        )
        assert user.is_superuser

    def test_create_superuser_staff_access_granted(
        self, user_data: User, raw_password: str
    ) -> None:
        user = User.objects.create_superuser(
            email=user_data.email, password=raw_password
        )
        assert user.is_staff

    def test_create_superuser_admin_role_granted(
        self, user_data: User, raw_password: str
    ) -> None:
        user = User.objects.create_superuser(
            email=user_data.email, password=raw_password
        )
        assert user.role == UserRoles.ADMIN


class TestUserManager:
    def test_create_user_user_role_granted(
        self, user_data: User, raw_password: str
    ) -> None:
        user = User.objects.create_user(email=user_data.email, password=raw_password)
        assert user.role == UserRoles.USER

    def test_create_user_password_set_correctly(
        self, user_data: User, raw_password: str
    ) -> None:
        user = User.objects.create_user(email=user_data.email, password=raw_password)
        assert user.check_password(raw_password)

from apps.users.constants import UserRoles
from apps.users.models import User


class TestSuperuserManager:
    def test_create_superuser_superuser_access_granted(self) -> None:
        user = User.objects.create_superuser(
            email="admin@example.com", password="password"
        )
        assert user.is_superuser

    def test_create_superuser_staff_access_granted(self) -> None:
        user = User.objects.create_superuser(
            email="admin@example.com", password="password"
        )
        assert user.is_staff

    def test_create_superuser_admin_role_granted(self) -> None:
        user = User.objects.create_superuser(
            email="admin@example.com", password="password"
        )
        assert user.role == UserRoles.ADMIN


class TestUserManager:
    def test_create_user_user_role_granted(self) -> None:
        user = User.objects.create_user(email="user@example.com", password="password")
        assert user.role == UserRoles.USER

    def test_create_user_password_set_correctly(self) -> None:
        user = User.objects.create_user(email="user@example.com", password="password")
        assert user.check_password("password")

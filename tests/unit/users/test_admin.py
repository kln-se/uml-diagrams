from unittest.mock import Mock

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from apps.users.admin import CustomUserAdmin
from apps.users.constants import UserRoles
from apps.users.models import User
from tests.factories import UserFactory


@pytest.fixture
def user_form(mocker: MockerFixture) -> Mock:
    """
    Return a mocked UserForm object.
    From contains entered raw password.
    """
    faker_obj = Faker()
    mocker_obj = mocker.Mock()
    mocker_obj.cleaned_data = {"password": faker_obj.password()}
    return mocker_obj


@pytest.fixture
def wsgi_request(mocker: MockerFixture) -> Mock:
    """Return a mocked WSGIRequest object."""
    return mocker.Mock()


@pytest.fixture
def custom_user_admin(mocker: MockerFixture) -> CustomUserAdmin:
    """
    Return a CustomUserAdmin object.
    It's used to test internal save_model() method.
    """
    admin = CustomUserAdmin(mocker.Mock(), mocker.Mock())
    return admin


def test_save_model_check_password_hashing_when_user_created(
    wsgi_request: Mock, user_form: Mock, custom_user_admin: CustomUserAdmin
):
    """
    GIVEN a user to be created via admin panel
    WHEN save_model() method is called
    THEN check that user is created and its password is hashed.
    """
    new_user_data = UserFactory.build(role=UserRoles.USER)
    custom_user_admin.save_model(
        request=wsgi_request, obj=new_user_data, form=user_form, change=False
    )
    assert User.objects.filter(id=new_user_data.id).exists()
    created_user = User.objects.get(id=new_user_data.id)
    assert created_user.check_password(user_form.cleaned_data["password"])


def test_save_model_check_password_hashing_when_user_updated(
    wsgi_request: Mock, user_form: Mock, custom_user_admin: CustomUserAdmin
):
    """
    GIVEN a user to be updated via admin panel
    WHEN save_model() method is called
    THEN check that's user password is updated and hashed.
    """
    existing_user = UserFactory()
    custom_user_admin.save_model(
        request=wsgi_request, obj=existing_user, form=user_form, change=True
    )
    assert existing_user.check_password(user_form.cleaned_data["password"])

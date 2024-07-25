import pytest
from rest_framework import serializers

from apps.users.constants import PASSWORD_MIN_LENGTH
from apps.users.validators import PasswordValidator
from tests.factories import FakePassword


def test_password_validator_min_length() -> None:
    password = FakePassword.generate(length=PASSWORD_MIN_LENGTH - 1)
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_length(
            value=password, min_length=PASSWORD_MIN_LENGTH
        )
    assert ex.value.detail[0].code == "password_too_short"


def test_password_validator_special_chars_required() -> None:
    password = FakePassword.generate(special_chars=False)
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_has_special_chars(value=password)
    assert ex.value.detail[0].code == "password_missing_special_chars"


def test_password_validator_uppercase_required() -> None:
    password = FakePassword.generate(upper_case=False)
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_is_uppercase(value=password)
    assert ex.value.detail[0].code == "password_missing_uppercase"


def test_password_validator_lowercase_required() -> None:
    password = FakePassword.generate(lower_case=False)
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_is_lowercase(value=password)
    assert ex.value.detail[0].code == "password_missing_lowercase"


def test_password_validator_digit_required() -> None:
    password = FakePassword.generate(digits=False)
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_is_digit(value=password)
    assert ex.value.detail[0].code == "password_missing_digit"


@pytest.mark.parametrize(
    ("password", "code"),
    [
        (FakePassword.generate(length=PASSWORD_MIN_LENGTH - 1), "password_too_short"),
        (FakePassword.generate(special_chars=False), "password_missing_special_chars"),
        (FakePassword.generate(upper_case=False), "password_missing_uppercase"),
        (FakePassword.generate(lower_case=False), "password_missing_lowercase"),
        (FakePassword.generate(digits=False), "password_missing_digit"),
    ],
)
def test_password_validator_complexity(password: str, code: str) -> None:
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_complexity(value=password)
    assert ex.value.detail[0].code == "password_too_simple"

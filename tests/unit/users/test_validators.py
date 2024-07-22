import pytest
from rest_framework import serializers

from apps.users.validators import PasswordValidator


def test_password_validator_min_length() -> None:
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_length(value="123aA.", min_length=8)
    assert ex.value.detail[0].code == "password_too_short"


def test_password_validator_special_chars_required() -> None:
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_has_special_chars(value="12345678aA")
    assert ex.value.detail[0].code == "password_missing_special_chars"


def test_password_validator_uppercase_required() -> None:
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_is_uppercase(value="12345678a.")
    assert ex.value.detail[0].code == "password_missing_uppercase"


def test_password_validator_lowercase_required() -> None:
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_is_lowercase(value="12345678A.")
    assert ex.value.detail[0].code == "password_missing_lowercase"


def test_password_validator_digit_required() -> None:
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_is_digit(value="aaaaaaaaA.")
    assert ex.value.detail[0].code == "password_missing_digit"


@pytest.mark.parametrize(
    ("password", "code"),
    [
        ("123aA.", "password_too_short"),
        ("12345678aA", "password_missing_special_chars"),
        ("12345678a.", "password_missing_uppercase"),
        ("12345678A.", "password_missing_lowercase"),
        ("aaaaaaaaA.", "password_missing_digit"),
    ],
)
def test_password_validator_complexity(password: str, code: str) -> None:
    with pytest.raises(serializers.ValidationError) as ex:
        PasswordValidator.validate_complexity(value=password)
    assert ex.value.detail[0].code == "password_too_simple"

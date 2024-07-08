import re

from rest_framework import serializers

from apps.users.constants import PASSWORD_MIN_LENGTH, PASSWORD_SPECIAL_CHARS


class PasswordValidator:
    @staticmethod
    def validate_length(value: str, min_length: int = PASSWORD_MIN_LENGTH) -> str:
        if len(value) < min_length:
            raise serializers.ValidationError(
                f"Password must be at least {min_length} characters long."
            )
        return value

    @staticmethod
    def validate_has_special_chars(
        value: str, special_chars: str = PASSWORD_SPECIAL_CHARS
    ) -> str:
        if not any(char in special_chars for char in value):
            raise serializers.ValidationError(
                f"Password must contain at least one special character: "
                f"{special_chars}."
            )
        return value

    @staticmethod
    def validate_is_digit(value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one digit."
            )
        return value

    @staticmethod
    def validate_is_lowercase(value: str) -> str:
        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter."
            )
        return value

    @staticmethod
    def validate_is_uppercase(value: str) -> str:
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        return value

    @staticmethod
    def validate_complexity(value: str) -> str:
        pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*["
            + PASSWORD_SPECIAL_CHARS
            + r"])[A-Za-z\d"
            + PASSWORD_SPECIAL_CHARS
            + r"]{8,}$"
        )

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter, "
                "one uppercase letter, one digit, and one special character."
            )
        return value

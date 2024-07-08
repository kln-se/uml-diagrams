from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.users.models import User
from apps.users.validators import PasswordValidator


class SignupUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[
            PasswordValidator.validate_length,
            PasswordValidator.validate_has_special_chars,
            PasswordValidator.validate_is_digit,
            PasswordValidator.validate_is_lowercase,
            PasswordValidator.validate_is_uppercase,
        ],
    )

    class Meta:
        model = User
        fields = ["id", "email", "password", "first_name", "last_name"]
        read_only_fields = ["id"]

    def create(self, validated_data: dict[str, str]) -> User:
        user = User.objects.create_user(**validated_data)
        return user

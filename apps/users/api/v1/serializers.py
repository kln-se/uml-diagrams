from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.users.models import User
from apps.users.validators import PasswordValidator


class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    role = serializers.ReadOnlyField()
    email = serializers.EmailField(
        required=False, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        required=False,
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
        fields = ["id", "email", "password", "first_name", "last_name", "role"]
        read_only_fields = ["id", "role"]

    def update(self, instance: User, validated_data: dict[str, str]) -> User:
        instance.email = validated_data.get("email", instance.email)
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()
        return instance


class SignupUserSerializer(UserSerializer):
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

    def create(self, validated_data: dict[str, str]) -> User:
        user = User.objects.create_user(**validated_data)
        return user

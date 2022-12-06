from rest_framework import serializers

from users.validators import username_validator


class ValidateUsername:
    """Валидатор имени пользователя"""

    def validate_username(self, value):
        return username_validator(value)

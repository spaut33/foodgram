from api.mixins import ValidateUsername
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer, ValidateUsername):
    """Базовый клас сериализатора пользователей"""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class RegisterUserSerializer(BaseUserSerializer):
    """Сериализатор создания пользователей."""

    def validate_password(self, data):
        password = data
        errors = None
        try:
            password_validation.validate_password(password=password)
        except ValidationError as e:
            errors = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(data)

    def create(self, validated_data):
        with transaction.atomic():
            user = User(
                username=self.initial_data['username'],
                first_name=self.initial_data['first_name'],
                last_name=self.initial_data['last_name'],
                email=self.initial_data['email'],
            )
            user.set_password(self.initial_data['password'])
            user.save()
            return user

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('password',)
        extra_kwargs = {'password': {'write_only': True, 'required': True}}


class UserSerializer(BaseUserSerializer):
    """Сериализатор пользователей."""

    is_subscribed = SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.subscriptions.filter(
            subscription=user
        )

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('is_subscribed',)

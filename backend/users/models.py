from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import username_validator

ROLE_USER = 'user'
ROLE_ADMIN = 'admin'
ROLES = ((ROLE_USER, _('Пользователь')), (ROLE_ADMIN, _('Администратор')))


class UserManager(BaseUserManager):
    """Настройка прав доступа для админов"""


class User(AbstractUser):
    """Кастомная модель пользователя"""

    username = models.CharField(
        _('username'),
        max_length=settings.USERNAME_LENGTH,
        unique=True,
        validators=(username_validator,),
    )
    email = models.EmailField(
        _('email address'), max_length=settings.EMAIL_LENGTH, unique=True
    )
    first_name = models.CharField(
        _('first name'), max_length=settings.USER_FIRSTNAME_LENGTH, blank=True
    )
    last_name = models.CharField(
        _('last name'), max_length=settings.USER_LASTNAME_LENGTH, blank=True
    )
    password = models.CharField(
        _('password'), max_length=settings.USER_PASSWORD_LENGTH
    )

    @property
    def is_admin(self):
        return self.is_superuser or self.is_staff


class Subscription(models.Model):
    """Модель подписки пользователей на пользователей."""

    MODEL_STRING = '{user} подписан на {another_user}'
    IS_CLEAR = False

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    subscription = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Юзер, на кого подписываются',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscription'],
                name='Unique user subscription',
            )
        ]

    def __str__(self):
        return self.MODEL_STRING.format(
            user=self.user.get_username(),
            another_user=self.subscription.get_username(),
        )

    def save(self, *args, **kwargs):
        if not self.IS_CLEAR:
            self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        self.IS_CLEAR = True
        if (
            self.subscription
            and self.subscription.get_username() == self.user.get_username()
        ):
            raise ValidationError(
                'Пользователь не может быть подписан на себя!'
            )
        return super().clean()

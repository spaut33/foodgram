import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

LEGAL_CHARACTERS = re.compile(r'[\w.@+-]')


def username_validator(value):
    """Проверка на запрещенные слова в имени."""
    forbidden_chars = ''.join(set(LEGAL_CHARACTERS.sub('', value)))
    if forbidden_chars:
        raise ValidationError(
            _(
                f'Нельзя использовать символ(ы): {forbidden_chars} в имени '
                f'пользователя.'
            )
        )
    return value

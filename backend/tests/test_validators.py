import pytest
from django.core.exceptions import ValidationError

from users.validators import username_validator


class TestValidators:
    @pytest.mark.parametrize('wrong_username', ['user$@fake', '@#$%^$$ssdf'])
    def test_wrong_username_validator(self, wrong_username):
        with pytest.raises(ValidationError):
            assert username_validator(wrong_username) == False, (
                f'Ошибка в работе валидатора на имени {wrong_username}'
            )

    def test_right_username_validator(self):
        right_username = 'right_username'
        assert bool(username_validator(right_username)) == True, (
            f'Ошибка в работе валидатора на имени {right_username}'
        )
import pytest

from recipes.admin import RecipeAdmin
from recipes.models import Favorite


@pytest.mark.django_db
class TestAdminSite:
    """Тест администраторской части проекта"""

    def test_favorites_count(self, user, recipe):
        assert RecipeAdmin.favorites_count(self, recipe) == 0, (
            'Если рецепт не добавлен в избранное, то количество в столбце '
            '`Добавлений в избранное` должно быть 0'
        )
        Favorite.objects.create(user=user, recipe=recipe)
        assert RecipeAdmin.favorites_count(self, recipe) == 1, (
            'Если рецепт добавлен в избранное 1 раз, то количество в столбце '
            '`Добавлений в избранное` должно быть 1'
        )

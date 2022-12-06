import pytest

from recipes.models import Favorite, Ingredient, Unit, Recipe, Tag
from users.models import Subscription


@pytest.fixture
def measurement_unit():
    return Unit.objects.create(name='m.unit')


@pytest.fixture
def ingredient(measurement_unit):
    return Ingredient.objects.create(
        name='Secret ingredient', measurement_unit=measurement_unit
    )


@pytest.fixture
def recipe(user):
    return Recipe.objects.create(name='Delicious Fried Chicken', author=user)


@pytest.fixture
def favorite(user, recipe):
    return Favorite.objects.create(recipe=recipe, user=user)


@pytest.fixture
def tag():
    return Tag.objects.create(name='test-tag')


@pytest.fixture
def subscription(user, another_user):
    return Subscription.objects.create(user=user, subscription=another_user)

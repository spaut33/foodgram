import pytest

from recipes.models import Favorite, Ingredient, Unit, Recipe


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
    return Recipe.objects.create(name='Delicious Fried Chicken', user=user)


@pytest.fixture
def favorite(user, recipe):
    return Favorite.objects.create(recipe=recipe, user=user)

import pytest

from recipes.models import (
    Favorite,
    Ingredient,
    Unit,
    Recipe,
    Tag,
    ShoppingCart,
)
from users.models import Subscription


@pytest.fixture
def tag():
    return Tag.objects.create(
        name='test-tag', slug='test-tag', color='#fff000'
    )


@pytest.fixture
def tag2():
    return Tag.objects.create(
        name='test-tag-2', slug='test-tag-2', color='#000aaa'
    )


@pytest.fixture
def measurement_unit():
    return Unit.objects.create(name='m.unit')


@pytest.fixture
def ingredient(measurement_unit):
    return Ingredient.objects.create(
        name='Secret ingredient 1', measurement_unit=measurement_unit
    )


@pytest.fixture
def ingredient2(measurement_unit):
    return Ingredient.objects.create(
        name='Secret ingredient 2', measurement_unit=measurement_unit
    )


@pytest.fixture
def ingredient3(measurement_unit):
    return Ingredient.objects.create(
        name='Secret ingredient 3', measurement_unit=measurement_unit
    )


@pytest.fixture
def recipe(user, ingredient, tag):

    recipe = Recipe.objects.create(
        name='Delicious Fried Test Chicken', author=user, cooking_time=10
    )

    recipe.tags.add(tag)
    return recipe


@pytest.fixture
def recipe_with_ingredients(recipe, ingredient, ingredient2, ingredient3):
    recipe.recipe_ingredients.create(ingredient=ingredient, amount=100)
    recipe.recipe_ingredients.create(ingredient=ingredient2, amount=200)
    recipe.recipe_ingredients.create(ingredient=ingredient3, amount=300)
    return recipe


@pytest.fixture
def favorite(user, recipe):
    return Favorite.objects.create(recipe=recipe, user=user)


@pytest.fixture
def shopping_cart(user, recipe_with_ingredients):
    shopping_cart = ShoppingCart.objects.create(
        user=user, recipe=recipe_with_ingredients
    )
    return shopping_cart


@pytest.fixture
def subscription(user, another_user):
    return Subscription.objects.create(user=user, subscription=another_user)


@pytest.fixture
def image_str():
    return (
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYA'
        'AAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg'
        '=='
    )

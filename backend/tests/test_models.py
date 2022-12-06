import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
    Unit,
)
from users.models import Subscription

User = get_user_model()

MODEL_FIELDS = [
    [User, ['username', 'first_name', 'last_name', 'password']],
    [Recipe, ['author_id', 'name', 'image', 'text', 'cooking_time']],
    [Ingredient, ['name', 'measurement_unit_id']],
    [Tag, ['name', 'slug', 'color']],
    [Unit, ['name']],
    [RecipeIngredient, ['recipe_id', 'ingredient_id', 'amount']],
    [Subscription, ['user_id', 'subscription_id']],
    [Favorite, ['user_id', 'recipe_id']],
    [ShoppingCart, ['user_id', 'date_added']],
]

MODEL_M2M_FIELDS = [
    [Recipe, ['tags', 'ingredients']],
    [ShoppingCart, ['recipe']],
]


def search_field(fields, attname):
    for field in fields:
        if attname == field.attname:
            return field
    return None

def find_verbose_name(fields):
    for field in fields:
        if field.verbose_name is not None:
            return field
        return None


@pytest.mark.django_db
class TestModels:
    @pytest.mark.parametrize(
        argnames=['model_name', 'expected_fields'], argvalues=MODEL_FIELDS
    )
    def test_model_fields(self, model_name, expected_fields):
        """Test user model specific fields"""
        model_fields = model_name._meta.fields
        for test_field in expected_fields:
            field = search_field(model_fields, test_field)
            assert (
                field is not None
            ), f'Поле {test_field} не найдено в модели {model_name}'

    @pytest.mark.parametrize(
        argnames=['model_name', 'expected_fields'], argvalues=MODEL_M2M_FIELDS
    )
    def test_model_m2m_fields(self, model_name, expected_fields):
        """Test user model m2m specific fields"""
        model_fields = model_name._meta.many_to_many
        for test_field in expected_fields:
            field = search_field(model_fields, test_field)
            assert (
                field is not None
            ), f'Поле {test_field} не найдено в модели {model_name}'

    def test_ingredient_constraints(self, ingredient, measurement_unit):
        """Test model Ingredient constraints"""
        with pytest.raises(IntegrityError):
            Ingredient.objects.create(
                name='Secret ingredient', measurement_unit=measurement_unit
            )

    def test_favorite_constraints(self, favorite, recipe, user):
        """Test model Favorite constraints"""
        with pytest.raises(IntegrityError):
            Favorite.objects.create(recipe=recipe, user=user)

    @pytest.mark.parametrize(
        argnames=['model_name', 'test_fields'], argvalues=MODEL_FIELDS
    )
    def test_fields_verbose_names(self, model_name, test_fields):
        """Test all model fields has verbose names"""
        model_fields = model_name._meta.fields
        for test_field in test_fields:
            field = search_field(model_fields, test_field)
            assert (
                    field is not None
            ), f'Поле {test_field} не найдено в модели {model_name}'

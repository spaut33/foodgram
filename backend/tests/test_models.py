import pytest

from django.contrib.auth import get_user_model

from users.models import Subscription

User = get_user_model()

MODEL_FIELDS = [
    [User, ['username', 'first_name', 'last_name', 'password']],
    # [Recipe, ['user', 'name', 'image', 'description', 'cooking_time']],
    # [Ingredient, ['name', 'measurement_unit']],
    # [Tag, ['name', 'slug', 'color']],
    # [Unit, ['name']],
    # [RecipeIngredient, ['recipe', 'ingredient', 'amount']],
    [Subscription, ['user_id', 'subscription_id']],
    # [Favorite, ['user', 'recipe']],
    # [ShoppingCart, ['user', 'recipe']],
]


def search_field(fields, attname):
    for field in fields:
        if attname == field.attname:
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

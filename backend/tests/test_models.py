import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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
                name='Secret ingredient 1', measurement_unit=measurement_unit
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

    def test_is_admin_method(self, user, admin):
        """Тест атрибута is_admin модели User"""
        assert (
            user.is_admin is False
        ), 'Обычный юзер не должен обладать свойством is_admin'
        assert (
            admin.is_admin is True
        ), 'Админ с правами админа должен обладать свойством is_admin'

    def test_model_subscription_str(self, user, another_user, subscription):
        """Тест метода __str__ для модели Subscription"""
        assert (
            str(subscription) == f'{user.get_username()} подписан '
            f'на {another_user.get_username()}'
        )

    def test_model_tag_str(self):
        """Тест метода __str__ для модели Tag"""
        tag_with_long_name = Tag.objects.create(name='a' * 100)
        assert (
            str(tag_with_long_name) == 'a' * 15
        ), 'Имя модели Tag должно содержать 15 символов'

    def test_model_unit_str(self):
        """Тест метода __str__ для модели Unit"""
        unit_with_long_name = Unit.objects.create(name='u' * 100)
        assert (
            str(unit_with_long_name) == 'u' * 15
        ), 'Имя модели Unit должно содержать 15 символов'

    def test_model_ingredient_str(self, measurement_unit):
        """Тест метода __str__ для модели Ingredient"""
        # Для ингредиентов делаем первую букву большой и возвращаем вместе
        # с ед. изм.
        ingredient_with_long_name = Ingredient.objects.create(
            name='a' * 100, measurement_unit=measurement_unit
        )
        assert str(ingredient_with_long_name) == (
            'a' * 30
        ).capitalize() + ', ' + str(measurement_unit), (
            'Имя модели Ingredient должно содержать не более 30 символов имени '
            'ингредиента и не более 15 символов единицы измерения'
        )

    def test_model_shoppingcart_str(self, user, recipe):
        """Тест метода __str__ для модели ShoppingCart"""
        shoppingcart = ShoppingCart.objects.create(user=user, recipe=recipe)
        assert str(shoppingcart) == f'Список покупок пользователя {user}'

    def test_model_favorite_str(self, user, recipe):
        """Тест метода __str__ для модели Favorite"""
        favorite = Favorite.objects.create(recipe=recipe, user=user)
        assert (
            str(favorite)
            == f'Избранный рецепт Delicious Fried Test Chicken юзера test_user'
        )

    def test_self_subscription(self, user):
        """Тест подписки юзера на самого себя"""
        with pytest.raises(ValidationError):
            Subscription.objects.create(user=user, subscription=user), (
                'Подписка на самого себя должна бросать '
                'исключение ValidationError'
            )

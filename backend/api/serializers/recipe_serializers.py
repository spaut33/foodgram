from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import fields, serializers
from rest_framework.exceptions import ValidationError

from api.fields import Base64ImageField
from api.serializers import user_serializers
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class BaseIngredientSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор ингредиентов. Используется для форматирования имени
    """

    def validate_name(self, value):
        return value.capitalize()

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        data['name'] = (
            data['name'].capitalize() if data['name'] else data['name']
        )
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(BaseIngredientSerializer):
    """Сериализатор ингредиентов."""

    # measurement_unit должен содержать имя из м2м модели, для корректного
    # отображения
    measurement_unit = serializers.CharField(source='measurement_unit.name')

    class Meta:
        model = Ingredient
        fields = '__all__'
        order_by = ('-name',)


class RecipeIngredientsSerializer(BaseIngredientSerializer):
    """Сериализатор ингредиентов рецепта"""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit.name'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(BaseIngredientSerializer):
    """Сериализатор для создания ингредиентов рецепта"""

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(
        write_only=True,
        validators=[MinValueValidator(settings.INGREDIENT_MIN_VALUE)],
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""

    image = Base64ImageField()
    is_favorited = fields.SerializerMethodField(default=False)
    is_in_shopping_cart = fields.SerializerMethodField(default=False)
    tags = TagSerializer(many=True)
    author = user_serializers.UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        source='recipe_ingredients', many=True
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        # Проверка на is_authenticated, иначе для анонимов
        # будет ошибка
        return (
            user.is_authenticated
            and user.favorite_recipes.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        # Проверка на is_authenticated, иначе для анонимов
        # будет ошибка
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(recipe=obj, user=user).exists()
        )


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    """Укороченный сериализатор рецепта для отображения в подписках"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeCreateSerializer(RecipeSerializer):
    """Сериализатор для создания рецепта"""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta(RecipeSerializer.Meta):
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                {
                    'ingredients': _(
                        'Необходимо указать хотя бы один ингредиент.'
                    )
                }
            )
        if 'tags' not in data:
            raise serializers.ValidationError(
                {'tags', _('Необходимо указать хотя бы один тег.')}
            )
        return data

    def validate_ingredients(self, value):
        """Проверка, что ингредиент не повторяется"""
        ingredients_ids = [ingredient['id'] for ingredient in value]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                _('Ингредиенты не должны повторяться.')
            )
        return value

    def validate_cooking_time(self, value):
        """Проверка что время приготовления больше 0"""
        if value < 1:
            raise serializers.ValidationError(
                _('Время приготовления должно быть больше 0.')
            )
        return value

    def validate_tags(self, value):
        """Проверка что теги не повторяются"""
        if not value:
            raise serializers.ValidationError(
                _('Необходимо указать хотя бы один тег')
            )
        tags = [tag.id for tag in value]
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(_('Теги не должны повторяться.'))
        return value

    def create_ingredients(self, recipe, ingredients):
        """Создает ингредиенты для рецепта"""
        try:
            RecipeIngredient.objects.bulk_create(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient, id=ingredient['id']
                    ),
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            )
        except IntegrityError as error:
            raise ValidationError(
                _(f'Ошибка при добавлении ингредиента: {error}')
            )

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(recipe, validated_data)
        recipe.ingredients.clear()
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def to_representation(self, recipe):
        return RecipeSerializer(
            recipe, context={'request': self.context['request']}
        ).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор списка избранных рецептов"""

    name = serializers.CharField(source='recipe.name')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')
    image = serializers.URLField(source='recipe.image.url')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'cooking_time')

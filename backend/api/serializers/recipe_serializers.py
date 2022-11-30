from rest_framework import fields, serializers

from recipes.models import Recipe, Tag, Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""

    is_favorited = fields.BooleanField(default=True)
    is_in_shopping_cart = fields.BooleanField(default=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

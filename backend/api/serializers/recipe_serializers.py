from rest_framework import fields, serializers

from api.fields import Base64ImageField
from api.serializers import user_serializers
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite, \
    ShoppingCart


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source='measurement_unit.name')

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""

    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = fields.SerializerMethodField(default=False)
    is_in_shopping_cart = fields.SerializerMethodField(default=False)
    tags = TagSerializer(many=True)
    author = user_serializers.UserSerializer()
    ingredients = RecipeIngredientsSerializer(
        source='recipe_ingredients', many=True
    )

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
        return (
            user.is_authenticated
            and user.favorite_recipes.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            ShoppingCart.objects.filter(recipes=obj, user=user).exists()
        )


class RecipeSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='recipe.name')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')
    image = serializers.URLField(source='recipe.image.url')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'cooking_time')

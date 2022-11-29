from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.serializers.recipe_serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
)
from recipes.models import Ingredient, Recipe, Tag


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""

    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()


class TagViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    """Вьюсет тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    """Вьюсет ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

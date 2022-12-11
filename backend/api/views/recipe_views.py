from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action

from api.filters import IngredientFilter, RecipeFilterSet
from api.mixins import FavoriteShoppingCartMixin
from api.pagination import LimitPagePagination
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers.recipe_serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    RecipeSubscribeSerializer,
    TagSerializer,
)
from recipes.models import Favorite, Ingredient, Recipe, Tag


class TagIngredientBaseViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    """Базовый вьюсет для тегов и ингредиентов"""

    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet, FavoriteShoppingCartMixin):
    """Вьюсет для рецептов"""

    serializer_class = RecipeSerializer
    create_serializer_class = RecipeCreateSerializer
    subscribe_serializers_class = RecipeSubscribeSerializer
    queryset = Recipe.objects.select_related('author').all()
    pagination_class = LimitPagePagination
    filterset_class = RecipeFilterSet
    permission_classes = (IsAdminAuthorOrReadOnly,)

    def get_serializer_class(self):
        """Возвращает нужный сериализатор в зависимости от http-метода"""
        if self.request.method in permissions.SAFE_METHODS:
            return self.serializer_class
        return self.create_serializer_class

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        # Добавление рецепта в избранное
        if request.method == 'POST':
            return self.add_recipe(request, pk=pk, model=Favorite)
        # Удаление рецепта из избранного
        return self.delete_recipe(request, pk=pk, model=Favorite)


class TagViewSet(TagIngredientBaseViewSet):
    """Вьюсет тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(TagIngredientBaseViewSet):
    """Вьюсет ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.select_related('measurement_unit').all()
    filterset_class = IngredientFilter

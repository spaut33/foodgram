from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilterSet
from api.pagination import LimitPagePagination
from api.serializers.recipe_serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSubscribeSerializer,
    RecipeCreateUpdateSerializer,
)
from recipes.models import Ingredient, Recipe, Tag, Favorite


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    serializer_class = RecipeSerializer
    create_serializer_class = RecipeCreateUpdateSerializer
    subscribe_serializers_class = RecipeSubscribeSerializer
    queryset = Recipe.objects.select_related('author').all()
    pagination_class = LimitPagePagination
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return self.serializer_class
        return self.create_serializer_class

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeSerializer(
            instance=serializer.instance, context={'request': self.request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            try:
                Favorite.objects.create(user=request.user, recipe=recipe)
                return Response(
                    self.subscribe_serializers_class(recipe).data,
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as error:
                return Response(
                    {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            try:
                Favorite.objects.get(user=request.user, recipe=recipe).delete()
            except ObjectDoesNotExist as error:
                return Response(
                    {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    """Вьюсет тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    """Вьюсет ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.select_related('measurement_unit').all()
    filterset_class = IngredientFilter
    pagination_class = None

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from api.filters import IngredientFilter, RecipeFilterSet
from api.pagination import LimitPagePagination
from api.serializers.recipe_serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSubscribeSerializer,
)
from recipes.models import Ingredient, Recipe, Tag, Favorite


class RecipeViewSet(ModelViewSet):
    """Вьюсет рецептов."""

    serializer_class = RecipeSerializer
    queryset = Recipe.objects.select_related('author').all()
    pagination_class = LimitPagePagination
    filterset_class = RecipeFilterSet

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            try:
                Favorite.objects.create(user=request.user, recipe=recipe)
                serializer = RecipeSubscribeSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
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


class TagViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    """Вьюсет тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    """Вьюсет ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.select_related('measurement_unit').all()
    filterset_class = IngredientFilter
    pagination_class = None

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilterSet
from api.pagination import LimitPagePagination
from api.permissions import IsAdminAuthorOrReadOnly
from api.serializers.recipe_serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSubscribeSerializer,
    RecipeCreateSerializer,
)
from recipes.models import Ingredient, Recipe, Tag, Favorite, RecipeIngredient


class TagIngredientBaseViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    """Базовый вьюсет для тегов и ингредиентов"""

    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""

    serializer_class = RecipeSerializer
    create_serializer_class = RecipeCreateSerializer
    subscribe_serializers_class = RecipeSubscribeSerializer
    queryset = Recipe.objects.select_related('author').all()
    pagination_class = LimitPagePagination
    filterset_class = RecipeFilterSet
    permission_classes = (IsAdminAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return self.serializer_class
        return self.create_serializer_class

    def create_ingredients(self, instance, ingredients):
        recipe_ingredients = (
            RecipeIngredient(
                recipe=instance,
                ingredient=get_object_or_404(Ingredient, id=ingredient['id']),
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        )
        try:
            RecipeIngredient.objects.bulk_create(recipe_ingredients)
        except IntegrityError as error:
            raise ValidationError(
                f'Ошибка при добавлении ингредиента: {error}'
            )

    def perform_create(self, serializer):
        ingredients = serializer.validated_data.pop('ingredients')
        tags = serializer.validated_data.pop('tags')
        recipe = serializer.save(
            **serializer.validated_data, author=self.request.user
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)

    def perform_update(self, serializer):
        data = serializer.validated_data
        ingredients = data.pop('ingredients')
        tags = serializer.validated_data.pop('tags')
        instance = serializer.save()
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.create_ingredients(instance, ingredients)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get('pk'))
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


class TagViewSet(TagIngredientBaseViewSet):
    """Вьюсет тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(TagIngredientBaseViewSet):
    """Вьюсет ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.select_related('measurement_unit').all()
    filterset_class = IngredientFilter

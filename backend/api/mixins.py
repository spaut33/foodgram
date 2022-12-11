from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe
from users.validators import username_validator


class FavoriteShoppingCartMixin:
    """Общий класс для избранного и списка покупок"""

    def add_recipe(self, request, *args, **kwargs):
        """Добавляет рецепт"""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        model = kwargs['model']
        user = request.user
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': _('Такой рецепт уже есть')},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.create(user=user, recipe=recipe)
        return Response(
            self.subscribe_serializers_class(recipe).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def delete_recipe(request, *args, **kwargs):
        """Удаляет рецепт"""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        model = kwargs['model']
        user = request.user
        if not model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'errors': _('Такого рецепта нет')},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ValidateUsername:
    """Валидатор имени пользователя"""

    def validate_username(self, value):
        return username_validator(value)

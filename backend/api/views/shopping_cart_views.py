from django.db import IntegrityError
from django.db.models import Sum
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers.recipe_serializers import RecipeSubscribeSerializer
from core.generate_pdf import PDFFile
from recipes.models import Recipe, ShoppingCart


class ShoppingCartViewSet(viewsets.GenericViewSet):
    """Вьюсет для списка покупок"""

    serializer_class = RecipeSubscribeSerializer
    queryset = ShoppingCart.objects.all()

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Метод обрабатывает список покупок"""
        recipe = get_object_or_404(Recipe, pk=pk)
        # Получаем или создаем список покупок для данного юзера
        shopping_cart, create_flag = ShoppingCart.objects.get_or_create(
            user=request.user
        )
        if request.method == 'POST':
            # Добавляем рецепт в созданный (или полученный) список покупок
            if shopping_cart.recipe.filter(id=recipe.id).exists():
                return Response(
                    {'errors': _('Рецепт уже в списке покупок')},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                shopping_cart.recipe.add(recipe)
            except IntegrityError as error:
                return Response(
                    {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                self.serializer_class(recipe).data,
                status=status.HTTP_201_CREATED,
            )
        # Удаление рецепта из списка покупок
        if not shopping_cart.recipe.filter(id=recipe.id).exists():
            return Response(
                {'errors': _('Рецепта нет в списке покупок')},
                status=status.HTTP_400_BAD_REQUEST,
            )
        shopping_cart.recipe.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        # Bug @ Django 3.2. Без указания order_by() ORM добавляет
        # принудительно GROUP BY recipes_recipe.date_added и из-за этого
        # ингредиенты не группируются по имени.
        # https://code.djangoproject.com/ticket/14357
        #
        try:
            cart = (
                request.user.shoppingcart.recipe.select_related(
                    'recipe_ingredients'
                )
                .values(
                    'ingredients__name', 'ingredients__measurement_unit__name'
                )
                .annotate(sum=Sum('recipe_ingredients__amount'))
                .order_by(Lower('ingredients__name'))
            )
        except Exception as error:
            return Response(
                {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )

        pdf_file = PDFFile()
        # Добавляем ингредиенты в PDF, имена предварительно капитализируем
        for ingredient in cart:
            pdf_file.add_item(
                [
                    ingredient['ingredients__name'].capitalize(),
                    ingredient['sum'],
                    ingredient['ingredients__measurement_unit__name'],
                ]
            )
        return HttpResponse(
            pdf_file.get_content(),
            content_type='application/pdf',
            status=status.HTTP_200_OK,
        )

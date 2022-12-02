from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers.recipe_serializers import RecipeSubscribeSerializer
from core.generate_pdf import PDFFile
from recipes.models import ShoppingCart, Recipe


class ShoppingCartViewSet(viewsets.GenericViewSet):
    """Вьюсет для списка покупок"""

    serializers_class = RecipeSubscribeSerializer

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Метод обрабатывает список покупок"""
        recipe = get_object_or_404(Recipe, pk=pk)
        # Получаем или создаем список покупок для данного юзера
        shopping_cart, _ = ShoppingCart.objects.get_or_create(
            user=request.user
        )
        if request.method == 'POST':
            # Добавляем рецепт в созданный (или полученный) список покупок
            try:
                shopping_cart.recipe.add(recipe)
            except IntegrityError as error:
                return Response(
                    {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                self.serializers_class(recipe).data,
                status=status.HTTP_201_CREATED,
            )
        # Удаление рецепта из списка покупок
        else:
            try:
                shopping_cart.recipe.remove(recipe)
            except ObjectDoesNotExist as error:
                return Response(
                    {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(permissions.AllowAny,),
    )
    def download_shopping_cart(self, request):
        # Bug possibly? Без указания order_by() ORM добавляет принудительно
        # GROUP BY recipes_recipe.date_added и из-за этого ингредиенты не
        # группируются по имени.
        cart = (
            request.user.shoppingcart.recipe.prefetch_related(
                'recipe_ingredients'
            )
            .values('ingredients__name', 'ingredients__measurement_unit__name')
            .annotate(sum=Sum('recipe_ingredients__amount'))
            .order_by()
        )
        pdf_file = PDFFile()
        for ingredient in cart:
            pdf_file.add_item(
                f"{ingredient['ingredients__name']}: {ingredient['sum']}, "
                f"{ingredient['ingredients__measurement_unit__name']}"
            )
        return HttpResponse(
            pdf_file.get_content(),
            content_type='application/pdf',
            status=status.HTTP_200_OK,
        )

from django.db.models import Sum
from django.db.models.functions import Lower
from django.http import HttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.mixins import FavoriteShoppingCartMixin
from api.serializers.recipe_serializers import RecipeSubscribeSerializer
from core.generate_pdf import PDFFile
from recipes.models import ShoppingCart


class ShoppingCartViewSet(viewsets.GenericViewSet, FavoriteShoppingCartMixin):
    """Вьюсет для списка покупок"""

    subscribe_serializers_class = RecipeSubscribeSerializer
    queryset = ShoppingCart.objects.all()

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        """Метод обрабатывает список покупок"""
        # Добавление рецепта в избранное
        if request.method == 'POST':
            return self.add_recipe(request, pk=pk, model=ShoppingCart)
        # Удаление рецепта из избранного
        return self.delete_recipe(request, pk=pk, model=ShoppingCart)

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
                request.user.shoppingcart.select_related('recipe_ingredients')
                .values(
                    'recipe__ingredients__name',
                    'recipe__ingredients__measurement_unit__name',
                )
                .annotate(sum=Sum('recipe__recipe_ingredients__amount'))
                .order_by(Lower('recipe__ingredients__name'))
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
                    ingredient['recipe__ingredients__name'].capitalize(),
                    ingredient['sum'],
                    ingredient['recipe__ingredients__measurement_unit__name'],
                ]
            )
        if not pdf_file.get_content():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(
            pdf_file.get_content(),
            content_type='application/pdf',
            status=status.HTTP_200_OK,
        )

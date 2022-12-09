from django.db import models
import django_filters
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтр поиска ингредиента."""

    name = django_filters.CharFilter(method='find_by_name')
    # issue #12
    # https://stackoverflow.com/questions/18235419/how-to-chain-django-querysets-preserving-individual-order

    def find_by_name(self, queryset, name, value):
        if not value:
            return queryset
        # Сначала ищем совпадения по началу слова, аннотируем значением
        # qs_order=0
        starts_with = queryset.filter(name__istartswith=value).annotate(
            qs_order=models.Value(0, models.IntegerField())
        )
        # Затем ищем совпадения по любому слову, выкидываем из них совпадения
        # по началу слова (они у нас уже есть) аннотируем значением
        # qs_order=1
        contains = (
            queryset.filter(name__icontains=value)
            .exclude(name__istartswith=value)
            .annotate(qs_order=models.Value(1, models.IntegerField()))
        )
        # Объединяем результаты, сортируя по qs_order
        return starts_with.union(contains).order_by('qs_order')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilterSet(filters.FilterSet):
    """Фильтр рецептов"""

    is_favorited = filters.BooleanFilter(method='get_favorite_recipes')
    is_in_shopping_cart = filters.BooleanFilter(method='get_shopping_cart')
    tags = filters.Filter(method='filter_tags')

    class Meta:
        model = Recipe
        fields = ('author',)

    def filter_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags', None)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset  # noqa: R504

    def get_favorite_recipes(self, queryset, name, value):
        """Фильтр рецептов, добавленных в избранное."""
        if value:
            queryset = self.queryset.filter(
                id__in=self.request.user.favorite_recipes.all().values_list(
                    'recipe__pk', flat=True
                )
            )
        return queryset  # noqa: R504

    def get_shopping_cart(self, queryset, name, value):
        """Фильтр рецептов, добавленных в список покупок."""
        if value:
            queryset = self.request.user.shoppingcart.recipe.all()
        return queryset  # noqa: R504

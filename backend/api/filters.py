import django_filters
from django_filters import rest_framework as filters
from django_filters.widgets import CSVWidget

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    """Фильтр поиска ингредиента."""

    name = django_filters.CharFilter(method='find_by_name')
    # TODO: нет поиска по вхождению. Добавить второй кверисет,
    #  объединить результаты. issue #12
    # https://stackoverflow.com/questions/18235419/how-to-chain-django-querysets-preserving-individual-order  # noqa

    def find_by_name(self, queryset, name, value):
        if not value:
            return queryset
        queryset_startswith = queryset.filter(name__istartswith=value)
        return queryset_startswith

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilterSet(filters.FilterSet):
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
        return queryset

    def get_favorite_recipes(self, queryset, name, value):
        """Фильтр рецептов, добавленных в избранное."""
        if value:
            queryset = self.queryset.filter(
                id__in=self.request.user.favorite_recipes.all().values_list(
                    'recipe__pk', flat=True
                )
            )
        return queryset

    def get_shopping_cart(self, queryset, name, value):
        """Фильтр рецептов, добавленных в список покупок."""
        if value:
            queryset = self.request.user.shoppingcart.recipe.all()
        return queryset

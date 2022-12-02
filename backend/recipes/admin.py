
from django.contrib import admin

from recipes.models import (
    Ingredient,
    Tag,
    Unit,
    Recipe,
    RecipeIngredient,
    Favorite,
)
from users.models import Subscription


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_editable = ('color',)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_editable = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_editable = ('measurement_unit',)


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 2


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'text', 'cooking_time', 'author', 'date_added')
    readonly_fields = ('date_added',)
    inlines = (RecipeIngredientInLine,)


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('recipe__name', 'user__username')

@admin.register(Subscription)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription')
from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from django.utils.translation import gettext_lazy as _


User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=settings.TAG_MAX_LENGTH,
        verbose_name=_('Название'),
        db_index=True,
    )
    color = ColorField(format='hex', default='#FFFFFF')
    slug = models.SlugField(
        unique=True, max_length=settings.MAX_TAG_SLUG_LENGTH
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ('name',)

    def __str__(self):
        return self.name[:15]


class Unit(models.Model):
    """Модель единиц измерения."""

    name = models.CharField(
        max_length=settings.UNIT_NAME_MAX_LENGTH,
        verbose_name=_('Название'),
        unique=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _('Единица измерения')
        verbose_name_plural = _('Единицы измерения')
        ordering = ('name',)

    def __str__(self):
        return self.name[:15]


class Ingredient(models.Model):
    """Модель ингредиента."""

    MODEL_STRING = _('{name:.30}, {measurement_unit}')

    name = models.CharField(
        max_length=settings.INGREDIENT_NAME_MAX_LENGTH,
        verbose_name=_('Название'),
        null=False,
        db_index=True,
    )
    measurement_unit = models.ForeignKey(
        Unit,
        related_name='ingredients',
        verbose_name=_('Единицы измерения'),
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='Unique ingredient with unit',
            )
        ]
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        ordering = ('name',)

    def __str__(self):
        return self.MODEL_STRING.format(
            name=self.name.capitalize(), measurement_unit=self.measurement_unit
        )


class Recipe(models.Model):
    """Модель рецепта."""

    MODEL_STRING = _('{name:.50}')

    name = models.CharField(
        max_length=settings.RECIPE_NAME_MAX_LENGTH,
        verbose_name=_('Название'),
        null=False,
        db_index=True,
    )
    text = models.TextField(verbose_name=_('Описание'))
    image = models.ImageField(
        verbose_name=_('Изображение'), upload_to='recipes/images/'
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('Время приготовления, мин.'),
        validators=[MinValueValidator(settings.RECIPE_MIN_COOKING_TIME)],
        null=False,
    )
    date_added = models.DateTimeField(
        verbose_name=_('Дата добавления'), auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор'),
        null=False,
    )
    # M2M Models
    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name=_('Теги')
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name=_('Ингредиенты'),
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')
        ordering = ('-date_added',)

    def __str__(self):
        return self.MODEL_STRING.format(
            name=self.name
        )


class RecipeIngredient(models.Model):
    """Модель количества ингредиента для рецепта."""

    MODEL_STRING = '{ingredient:.30}: {amount} {unit}'

    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        verbose_name=_('Рецепт'),
        on_delete=models.CASCADE,
        db_index=True,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        verbose_name=_('Ингредиент'),
        on_delete=models.CASCADE,
        db_index=True,
    )
    amount = models.PositiveSmallIntegerField(verbose_name=_('Количество'))

    class Meta:
        verbose_name = _('Ингредиенты рецепта')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.MODEL_STRING.format(
            ingredient=self.ingredient.name,
            amount=self.amount,
            unit=self.ingredient.measurement_unit,
        )


class Favorite(models.Model):
    """Модель избранных рецептов юзера"""

    MODEL_STRING = 'Избранный рецепт {recipe:.30} юзера {user}'

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Избранный рецепт'),
        related_name='favorites',
        db_index=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Пользователь'),
        related_name='favorite_recipes',
        db_index=True,
    )
    date_added = models.DateTimeField(
        verbose_name=_('Дата добавления'), auto_now_add=True, db_index=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='Unique recipe with user'
            )
        ]
        verbose_name = _('Избранный рецепт')
        verbose_name_plural = _('Избранные рецепты')
        ordering = ('-date_added',)

    def __str__(self):
        return self.MODEL_STRING.format(
            recipe=self.recipe.name, user=self.user.get_username()
        )


class ShoppingCart(models.Model):
    """Модель список покупок пользователя"""

    user = models.OneToOneField(
        User,
        related_name='shoppingcart',
        on_delete=models.CASCADE,
        db_index=True,
    )
    recipe = models.ManyToManyField(
        Recipe, related_name='shoppingcart_recipes', db_index=True
    )
    date_added = models.DateTimeField(
        verbose_name=_('Дата добавления'), auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = _('Список покупок')
        verbose_name_plural = _('Списки покупок')

    def __str__(self):
        return _('Список покупок пользователя {user}').format(
            user=self.user.get_username()
        )

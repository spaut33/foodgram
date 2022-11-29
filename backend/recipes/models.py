from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=settings.TAG_MAX_LENGTH, verbose_name=_('Название')
    )
    color = ColorField(format='hex', default='#FFFFFF')
    slug = models.SlugField(
        unique=True, max_length=settings.MAX_TAG_SLUG_LENGTH
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')

    def __str__(self):
        return self.name[:15]


class Unit(models.Model):
    """Модель единиц измерения."""

    name = models.CharField(
        max_length=settings.UNIT_NAME_MAX_LENGTH,
        verbose_name=_('Название'),
        unique=True,
    )

    class Meta:
        verbose_name = _('Единица измерения')
        verbose_name_plural = _('Единицы измерения')

    def __str__(self):
        return self.name[:15]


class Ingredient(models.Model):
    """Модель ингредиента."""

    MODEL_STRING = _('{name:.30}, {measurement_unit}')

    name = models.CharField(
        max_length=settings.INGREDIENT_NAME_MAX_LENGTH,
        verbose_name=_('Название'),
    )
    measurement_unit = models.ForeignKey(
        Unit,
        related_name='ingredients',
        verbose_name=_('Единицы измерения'),
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='Unique ingredient with unit'
            )
        ]
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')

    def __str__(self):
        return self.MODEL_STRING.format(
            name=self.name, measurement_unit=self.measurement_unit
        )


class Recipe(models.Model):
    """Модель рецепта."""

    MODEL_STRING = _('Рецепт {name:.30} автора {user}')

    name = models.CharField(
        max_length=settings.RECIPE_NAME_MAX_LENGTH, verbose_name=_('Название')
    )
    description = models.TextField(verbose_name=_('Описание'))
    image = models.ImageField(verbose_name=_('Изображение'))
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('Время приготовления'),
        validators=[MinValueValidator(settings.RECIPE_MIN_COOKING_TIME)],
    )
    date_added = models.DateTimeField(
        verbose_name=_('Дата добавления'), auto_now_add=True, db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор'),
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

    def __str__(self):
        return self.MODEL_STRING.format(
            name=self.name, user=self.user.get_username()
        )


class RecipeIngredient(models.Model):
    """Модель количества ингредиента для рецепта."""

    MODEL_STRING = _('Количества ингредиентов для рецепта {recipe:.30}')

    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        verbose_name=_('Рецепт'),
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_ingredients',
        verbose_name=_('Ингредиент'),
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')

    def __str__(self):
        return self.MODEL_STRING.format(recipe=self.recipe)

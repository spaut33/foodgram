from rest_framework.fields import SerializerMethodField

from .recipe_serializers import RecipeSubscribeSerializer
from .user_serializers import UserSerializer
from api.pagination import LimitPagePagination


class SubscriptionSerializer(UserSerializer):
    """Сериализатор подписок на пользователей."""

    recipes = RecipeSubscribeSerializer(many=True)
    recipes_count = SerializerMethodField()
    pagination_class = LimitPagePagination

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
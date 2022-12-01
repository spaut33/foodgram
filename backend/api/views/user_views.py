from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUsers
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import LimitPagePagination
from api.serializers import user_serializers

User = get_user_model()


class UserViewSet(DjoserUsers):
    """Пользователи на основе Djoser."""

    pagination_class = LimitPagePagination
    http_method_names = ('get', 'post', 'head')

    def subscribe(self):
        """Подписка на пользователя."""
        pass

    @action(methods=('get',), detail=False)
    def subscriptions(self, request):
        """Подписки пользователя."""
        queryset = User.objects.filter(subscribers__user=request.user)
        return Response(
            user_serializers.SubscriptionSerializer(
                queryset, context={'request': request}, many=True
            ).data
        )

    def reset_password(self, request, *args, **kwargs):
        return None

    def activation(self, request, *args, **kwargs):
        return None

    def resend_activation(self, request, *args, **kwargs):
        return None

    def reset_username(self, request, *args, **kwargs):
        return None

    def set_username(self, request, *args, **kwargs):
        return None

    def reset_password_confirm(self, request, *args, **kwargs):
        return None

    def reset_username_confirm(self, request, *args, **kwargs):
        return None

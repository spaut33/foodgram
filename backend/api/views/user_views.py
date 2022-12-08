from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUsers
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from api.pagination import LimitPagePagination
from api.serializers.subscribe_serializers import SubscriptionSerializer
from users.models import Subscription

User = get_user_model()


def get_subscription_serializer(*args, **kwargs):
    return SubscriptionSerializer(
        kwargs.get('queryset'),
        context={'request': kwargs.get('request')},
        many=True,
    ).data


class UserViewSet(DjoserUsers):
    """Пользователи на основе Djoser."""

    pagination_class = LimitPagePagination
    http_method_names = ('get', 'post', 'head')

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscriptions(self, request):
        """Список подписок пользователя."""

        # https://stackoverflow.com/questions/31785966/django-rest-framework-turn-on-pagination-on-a-viewset-like-modelviewset-pagina
        queryset = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(
                get_subscription_serializer(queryset=page, request=request)
            )
        return Response(
            get_subscription_serializer(queryset=queryset, request=request),
            status=status.HTTP_200_OK,
        )

    # Методы принудительно отключены для соответствия ТЗ
    #
    def reset_password(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def activation(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def resend_activation(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_username(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def set_username(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_password_confirm(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def reset_username_confirm(self, request, *args, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)


class SubscriptionViewSet(APIView):
    """Подписка и отписка пользователей."""

    permission_classes = (permissions.IsAuthenticated,)
    model = Subscription

    def post(self, request, *args, **kwargs):
        """Подписка на пользователя."""
        subscription = get_object_or_404(User, pk=kwargs.get('id'))
        try:
            self.model.objects.create(
                user=request.user, subscription=subscription
            )
        except ValidationError as error:
            return Response(
                {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            SubscriptionSerializer(
                subscription, context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, *args, **kwargs):
        """Отписка от пользователя."""
        subscription = get_object_or_404(User, pk=kwargs.get('id'))
        try:
            self.model.objects.get(
                user=request.user, subscription=subscription
            ).delete()
        except ObjectDoesNotExist as error:
            return Response(
                {'errors': str(error)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from users.models import Subscription
from .common import APITestBase

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestAPISubscriptions(APITestBase):
    def test_subscriptions_permissions(
        self, client, user_client, user, subscription
    ):
        """Test endpoint permissions"""
        subscriptions_url = self.urls['subscriptions']
        subscribe_url = self.urls['subscribe'].format(user_id=user.id)

        expected_responses = [
            [subscriptions_url, client.get, status.HTTP_401_UNAUTHORIZED],
            [subscribe_url, client.post, status.HTTP_401_UNAUTHORIZED],
            [subscriptions_url, user_client.get, status.HTTP_200_OK]
        ]
        for url, client_variant, code in expected_responses:
            response = client_variant(url)
            assert response.status_code == code, (
                f'Ошибка в коде ответа по адресу {url} клиента '
                f'{client_variant}, ожидался код ошибки {code}'
            )

    def test_create_subscription(
        self, client, user_client, user, another_user
    ):
        """Test creating subscription"""
        url = self.urls['subscribe'].format(user_id=another_user.id)
        wrong_url = self.urls['subscribe'].format(user_id=999999)
        self_subscribe_url = self.urls['subscribe'].format(user_id=user.id)
        expected_dict = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]
        self.assert_status_code(405, user_client.get(url), url=url)
        response = self.assert_status_code(201, user_client.post(url), url=url)

        self.assert_fields(expected_dict, response, url=url)

        assert response.data['is_subscribed'] == 1
        assert Subscription.objects.filter(
            user=user, subscription=another_user
        ).exists(), 'Подписка не создалась'

        # Nonexistent user subscription
        assert response.data['id'] == another_user.id
        self.assert_status_code(
            404, user_client.post(wrong_url), url=wrong_url
        ), 'Подписка на несуществующего юзера должна вернуть код 404'

        # Non-authorized user subscription
        self.assert_status_code(
            401, client.post(url), url=url
        ), 'Подписка неавторизованным юзером должна вернуть код 401'

        # Self subscription and repeat subscription
        self.assert_status_code(400, user_client.post(url), url=url)
        self.assert_status_code(
            400, user_client.post(self_subscribe_url), url=self_subscribe_url
        )

    def test_delete_subscription(
        self, client, user_client, user, some_users, another_user, subscription
    ):
        """Test delete user subscription"""
        url = self.urls['subscribe'].format(user_id=another_user.id)
        wrong_url = self.urls['subscribe'].format(user_id=999999)
        not_subscription_url = self.urls['subscribe'].format(
            user_id=some_users[0].id
        )
        assert (
            Subscription.objects.filter(
                user=user, subscription=another_user
            ).count()
            == 1
        )
        self.assert_status_code(204, user_client.delete(url), url=url)
        assert (
            Subscription.objects.filter(
                user=user, subscription=another_user
            ).count()
            == 0
        )
        # Delete non-existent subscription when user exists
        self.assert_status_code(
            400,
            user_client.delete(not_subscription_url),
            url=not_subscription_url,
        )
        # Delete subscription to non-existent user
        self.assert_status_code(
            404, user_client.delete(wrong_url), url=wrong_url
        )
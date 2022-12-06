import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

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
            [subscriptions_url, user_client.get, status.HTTP_200_OK],
            # TODO: Too complex, take into it in a separate test
            # [subscribe_url, client.post, status.HTTP_400_BAD_REQUEST],
        ]
        for url, client_variant, code in expected_responses:
            response = client_variant(url)
            assert response.status_code == code, (
                f'Ошибка в коде ответа по адресу {url} клиента '
                f'{client_variant}, ожидался код ошибки {code}'
            )

import pytest
from django.contrib.auth import get_user_model

from .common import APITestBase

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestUserAPI(APITestBase):
    def test_urls_anonymous_user(self, client, user, tag):
        """Test urls available for any users"""
        for url in self.urls.values():
            try:
                url = url.format(user_id=user.id, tag_id=tag.id)
            except KeyError:
                pass
            try:
                response = client.get(url)
            except Exception as e:
                assert (
                    False
                ), f'Страница `{url}` работает неправильно. Ошибка: `{e}`'
            assert (
                response.status_code != 404
            ), f'Адрес {url} не найден, проверьте этот адрес в urls.py'

    def test_users_anonymous_user(self, client, user_client):
        """Test api/users/ endpoint"""
        url = self.urls['users']
        response = self.assert_status_code(400, client.post(url), url=url)
        fields_required = ['username', 'email', 'password']
        self.assert_fields(fields_required, response, url=url)
        post_data = {
            'email': 'test@example.com',
            'username': 'test_username',
            'first_name': 'First',
            'last_name': 'Last',
            'password': 'test123FF$$',
        }
        # Удаляем всех юзеров перед тестом регистрации
        # Тест регистрации
        User.objects.all().delete()
        response = self.assert_status_code(
            201, client.post(url, post_data), url=url
        )
        assert User.objects.get(
            email=post_data['email'],
            username=post_data['username'],
            first_name=post_data['first_name'],
            last_name=post_data['last_name'],
        ), f'При запросе `{url}` пользователь не создался'
        assert (
            User.objects.count() == 1
        ), 'Неверное количество созданных юзеров, должно быть 1'
        fields_required = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        ]
        self.assert_fields(fields_required, response, url=url)

    def test_me_endpoint(self, client, user_client, user):
        """Test api/users/me/ endpoint"""
        url = self.urls['users_me']
        self.assert_status_code(401, client.get(url), url=url)
        self.assert_status_code(200, user_client.get(url), url=url)
        fields_required = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        ]
        response = self.assert_fields(
            fields_required, user.client.get(url), url=url
        )
        assert response.data == {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_subscribed': False,
            'username': user.username,
        }

    def test_user_profile(self, user_client, user, another_user):
        """Test user's profile"""
        url = self.urls['users_detail'].format(user_id=another_user.id)
        wrong_url = self.urls['users_detail'].format(user_id=999999999)
        self.assert_status_code(200, user_client.get(url), url=url)
        self.assert_status_code(404, user_client.get(wrong_url), url=wrong_url)

import pytest
from django.contrib.auth import get_user_model

from .common import APITestBase

User = get_user_model()


class TestUserAPI(APITestBase):
    @pytest.mark.django_db(transaction=True)
    def test_urls_anonymous_user(self, client, user):
        for url in APITestBase.urls.values():
            try:
                url.format(user_id=user.id)
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

    @pytest.mark.django_db(transaction=True)
    def test_user_anonymous_user(self, client, user):
        url = APITestBase.urls['users']
        response = client.post(url)
        code_expected = 400
        assert response.status_code == code_expected, (
            f'При запросе `{url}` без параметров должен возвращаться '
            f'код {code_expected}'
        )
        fields_required = ['username', 'email', 'password']
        for field in fields_required:
            assert field in response.json().keys(), (
                f'При запросе на {url} должны быть заполнены обязательные '
                f'поля. Не найдено поле {field}'
            )

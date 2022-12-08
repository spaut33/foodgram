import pytest
from django.contrib.auth import get_user_model

from .common import APITestBase

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestUserAPI(APITestBase):
    def test_urls_anonymous_user(self, client, user, tag, recipe, ingredient):
        """Test urls available for any users"""
        for url in self.urls.values():
            try:
                url = url.format(
                    user_id=user.id,
                    tag_id=tag.id,
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                )
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
        # Delete all users before testing registration.
        # Registration test
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
            fields_required, user_client.get(url), url=url
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

    def test_delete_user(self, user_client, user):
        """Test forbidden method destroy for user's endpoint"""
        url = self.urls['users_detail'].format(user_id=user.id)
        self.assert_status_code(405, user_client.delete(url), url=url)

    def test_disabled_joser_endpoints(self, user_client):
        """Disabled djoser's endpoints should return 404s"""
        disabled_endpoints = [
            'resend_activation/',
            'activation/',
            'reset_password/',
            'reset_username/',
            'set_username/',
            'reset_password_confirm/',
            'reset_username_confirm/',
        ]
        for url in disabled_endpoints:
            full_url = '/api/users/' + url
            self.assert_status_code(
                404, user_client.get(full_url), url=full_url
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
        self.assert_status_code(204, user_client.delete(url), url=url)
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

    def test_shopping_cart(
        self, client, user, user_client, recipe_with_ingredients
    ):
        """Test add recipe to shopping cart"""
        url = self.urls['recipe_in_cart'].format(
            recipe_id=recipe_with_ingredients.id
        )
        wrong_recipe_url = self.urls['recipe_in_cart'].format(
            recipe_id=999999999
        )
        # Get method not allowed
        self.assert_status_code(405, user_client.get(url), url=url)
        # POST of non-existent recipe
        self.assert_status_code(
            404, user_client.post(wrong_recipe_url), url=wrong_recipe_url
        )
        # Add recipe to shopping cart
        expected_dict = ['id', 'name', 'image', 'cooking_time']
        response = self.assert_status_code(201, user_client.post(url), url=url)
        self.assert_fields(expected_dict, response, url=url)
        # Add same recipe twice cause 400 error
        self.assert_status_code(400, user_client.post(url), url=url)
        assert response.data == {
            'id': recipe_with_ingredients.id,
            'name': recipe_with_ingredients.name,
            'image': None,
            'cooking_time': recipe_with_ingredients.cooking_time,
        }

    def test_delete_shopping_cart(
        self, client, user, user_client, recipe_with_ingredients
    ):
        """Test delete recipe from shopping cart"""
        url = self.urls['recipe_in_cart'].format(
            recipe_id=recipe_with_ingredients.id
        )
        wrong_recipe_url = self.urls['recipe_in_cart'].format(
            recipe_id=999999999
        )
        # DELETE of non-existent recipe
        self.assert_status_code(
            404, user_client.delete(wrong_recipe_url), url=wrong_recipe_url
        )
        # DELETE recipe from shopping cart
        user_client.post(url)
        self.assert_status_code(204, user_client.delete(url), url=url)
        # DELETE recipe twice from shopping cart
        self.assert_status_code(400, user_client.delete(url), url=url)

    def test_download_shopping_cart(
        self, client, admin_client, user_client, shopping_cart
    ):
        """Test download shopping cart list"""

        url = self.urls['shopping_cart']
        self.assert_status_code(400, admin_client.get(url), url=url)
        response = self.assert_status_code(200, user_client.get(url), url=url)
        assert response['Content-type'] == 'application/pdf'

from django.contrib.auth import get_user_model

import pytest

from api.serializers.recipe_serializers import IngredientSerializer
from recipes.models import Favorite, ShoppingCart, Recipe

from .common import APITestBase

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestAPI(APITestBase):
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

    def test_user_registration(self, client, user):
        """Test user registration"""
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
        url = self.urls['users']
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

    def test_password_validation(self, client):
        """Test password validation on user create"""
        url = self.urls['users']
        post_data = {
            'email': 'test@example.com',
            'username': 'test_username',
            'first_name': 'First',
            'last_name': 'Last',
            'password': '123',
        }
        # Fail create
        self.assert_status_code(400, client.post(url, post_data), url=url)
        assert (
            User.objects.count() == 0
        ), 'Неверное количество созданных юзеров, должно быть 0'

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
        assert (
            ShoppingCart.objects.filter(
                user=user, recipe=recipe_with_ingredients
            ).count()
            == 1
        )

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
        assert (
            ShoppingCart.objects.filter(
                user=user, recipe=recipe_with_ingredients
            ).count()
            == 0
        )
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

    def test_favorite_recipe(self, user_client, favorite):
        """Test add recipe to favorites"""

        url = self.urls['favorites'].format(recipe_id=favorite.recipe.id)
        wrong_recipe_url = self.urls['favorites'].format(recipe_id=999999999)

        # Get method not allowed
        self.assert_status_code(405, user_client.get(url), url=url)
        # POST of non-existent recipe
        self.assert_status_code(
            404, user_client.post(wrong_recipe_url), url=wrong_recipe_url
        )
        # Delete recipe from favorites
        self.assert_status_code(204, user_client.delete(url), url=url)
        assert (
            Favorite.objects.count() == 0
        ), 'Рецепт должен быть удален из избранного'

        # Add recipe to favorites
        expected_dict = ['id', 'name', 'image', 'cooking_time']
        response = self.assert_status_code(201, user_client.post(url), url=url)
        self.assert_fields(expected_dict, response, url=url)

        # Add same recipe twice cause 400 error
        self.assert_status_code(400, user_client.post(url), url=url)
        assert response.data == {
            'id': favorite.recipe.id,
            'name': favorite.recipe.name,
            'image': None,
            'cooking_time': favorite.recipe.cooking_time,
        }
        assert Favorite.objects.count() == 1, 'Рецепт должен быть добавлен'

        # Delete non-existent recipe from favorites
        Favorite.objects.all().delete()
        self.assert_status_code(400, user_client.delete(url), url=url)

    def test_tags(self, client, tag):
        """Test get tags list"""

        url = self.urls['tag_list']
        response = self.assert_status_code(200, client.get(url), url=url)
        expected_dict = ['id', 'name', 'color', 'slug']
        assert isinstance(response.data, list), 'Должен быть список тегов'
        self.assert_fields(expected_dict, response.data, url=url)

        url = self.urls['tag_detail'].format(tag_id=tag.id)
        wrong_url = self.urls['tag_detail'].format(tag_id=999999999)
        response = self.assert_status_code(200, client.get(url), url=url)
        self.assert_fields(expected_dict, response, url=url)
        self.assert_status_code(404, client.get(wrong_url), url=wrong_url)

    def test_ingredients(self, client, ingredient):
        """Test get ingredients list"""

        url = self.urls['ingredient_list']
        response = self.assert_status_code(200, client.get(url), url=url)
        expected_dict = ['id', 'name', 'measurement_unit']
        assert isinstance(
            response.data, list
        ), 'Должен быть список ингредиентов'
        self.assert_fields(expected_dict, response.data, url=url)

        url = self.urls['ingredient_detail'].format(
            ingredient_id=ingredient.id
        )
        wrong_url = self.urls['ingredient_detail'].format(
            ingredient_id=999999999
        )
        response = self.assert_status_code(200, client.get(url), url=url)
        self.assert_fields(expected_dict, response, url=url)
        self.assert_status_code(404, client.get(wrong_url), url=wrong_url)

    def test_ingredient_name(self, ingredient):
        """Test IngredientSerializer correctly formats name"""
        serializer = IngredientSerializer(ingredient)
        assert serializer.data['name'] == ingredient.name.capitalize()

    def test_recipe_list_get(self, client, recipe_with_ingredients):
        """Test get recipe list"""

        url = self.urls['recipe_list']
        response = self.assert_status_code(200, client.get(url), url=url)
        expected_dict = ['count', 'next', 'previous', 'results']
        self.assert_fields(expected_dict, response, url=url)
        # Проверим, что в ответе есть рецепт
        assert response.data['count'] > 0, 'Рецепт должен быть в ответе'
        expected_dict = [
            'id',
            'name',
            'image',
            'cooking_time',
            'author',
            'ingredients',
            'tags',
        ]
        self.assert_fields(expected_dict, response.data['results'], url=url)

    def test_recipe_get(self, client, recipe_with_ingredients, tag):
        """Test get recipe"""
        # Add tag to the recipe
        recipe_with_ingredients.tags.add(tag)
        url = self.urls['recipe_detail'].format(
            recipe_id=recipe_with_ingredients.id
        )
        wrong_url = self.urls['recipe_detail'].format(recipe_id=999999999)
        response = self.assert_status_code(200, client.get(url), url=url)
        expected_dict = [
            'id',
            'name',
            'image',
            'text',
            'cooking_time',
            'author',
            'ingredients',
            'tags',
        ]
        self.assert_fields(expected_dict, response, url=url)
        self.assert_status_code(404, client.get(wrong_url), url=wrong_url)

        # Test recipe has ingredients
        assert isinstance(
            response.data['ingredients'], list
        ), 'Должен быть список ингредиентов'
        expected_dict = ['id', 'name', 'measurement_unit', 'amount']
        self.assert_fields(
            expected_dict, response.data['ingredients'], url=url
        )

        # Test recipe has tags
        assert isinstance(
            response.data['tags'], list
        ), 'Должен быть список тегов'
        expected_dict = ['id', 'name', 'color', 'slug']
        self.assert_fields(expected_dict, response.data['tags'], url=url)

        # Test recipe content
        assert response.json() == {
            'id': recipe_with_ingredients.id,
            'name': recipe_with_ingredients.name,
            'image': None,
            'text': recipe_with_ingredients.text,
            'is_favorited': False,
            'is_in_shopping_cart': False,
            'cooking_time': recipe_with_ingredients.cooking_time,
            'author': {
                'id': recipe_with_ingredients.author.id,
                'username': recipe_with_ingredients.author.username,
                'email': recipe_with_ingredients.author.email,
                'first_name': recipe_with_ingredients.author.first_name,
                'last_name': recipe_with_ingredients.author.last_name,
                'is_subscribed': False,
            },
            'ingredients': [
                {
                    'id': ingredient.id,
                    'name': ingredient.name,
                    'measurement_unit': ingredient.measurement_unit.name,
                    'amount': recipe_with_ingredients.recipe_ingredients.get(
                        ingredient=ingredient
                    ).amount,
                }
                for ingredient in recipe_with_ingredients.ingredients.all()
            ],
            'tags': [
                {
                    'id': tag.id,
                    'name': tag.name,
                    'color': tag.color,
                    'slug': tag.slug,
                }
            ],
        }, 'Неверный контент рецепта'

    def test_create_recipe(
        self, user_client, ingredient, ingredient2, image_str, tag
    ):
        """Test recipe create"""
        url = self.urls['recipe_list']
        recipe_data = {
            'name': 'test_recipe',
            'text': 'test_text',
            'cooking_time': 100,
            'ingredients': [
                {'id': ingredient.id, 'amount': 101},
                {'id': ingredient2.id, 'amount': 102},
            ],
            'image': image_str,
            'tags': [tag.id],
        }
        response = self.assert_status_code(
            201, user_client.post(url, recipe_data, format='json'), url=url
        )
        expected_dict = [
            'id',
            'name',
            'image',
            'text',
            'cooking_time',
            'author',
            'ingredients',
            'tags',
        ]
        self.assert_fields(expected_dict, response, url=url)
        assert (
            Recipe.objects.get(id=response.data['id']).name
            == recipe_data['name']
        ), 'Неверное имя рецепта в базе данных'

    def test_update_recipe(self, user_client, recipe_with_ingredients, tag):
        """Test recipe update"""
        url = self.urls['recipe_detail'].format(
            recipe_id=recipe_with_ingredients.id
        )
        recipe_data = {
            'name': 'test_recipe_changed_name',
            'text': 'test_text',
            'cooking_time': 100,
            'tags': [tag.id],
            'ingredients': [
                {'id': ingredient.id, 'amount': 101}
                for ingredient in recipe_with_ingredients.ingredients.all()
            ],
        }
        response = self.assert_status_code(
            200, user_client.patch(url, recipe_data, format='json'), url=url
        )
        expected_dict = [
            'id',
            'name',
            'image',
            'text',
            'cooking_time',
            'author',
            'ingredients',
            'tags',
        ]
        self.assert_fields(expected_dict, response, url=url)
        assert (
            Recipe.objects.get(id=response.data['id']).name
            == recipe_data['name']
        ), 'Неверное имя рецепта в базе данных'

import pytest
from django.core.files.base import ContentFile

from api.fields import Base64ImageField
from tests.common import APITestBase


class TestUtils(APITestBase):
    def test_image_field(self, image_str):
        """Test Base64ImageField correctly converts base64 string to image"""
        field = Base64ImageField()
        assert isinstance(field.to_internal_value(image_str), ContentFile)

    @pytest.mark.django_db
    def test_ingredient_filter_by_name(self, client, ingredient, ingredient2):
        """Test that ingredient filter by name works correctly"""
        # name contains
        url = self.urls['ingredient_list'] + '?name=ingredient'
        response = client.get(url)
        self.assert_status_code(200, client.get(url), url=url)
        assert len(response.data) == 2
        # name startswith
        url = self.urls['ingredient_list'] + '?name=Secret'
        response = client.get(url)
        self.assert_status_code(200, client.get(url), url=url)
        assert len(response.data) == 2
        assert response.data[0]['name'] == 'Secret ingredient 1'
        # Test with empty name, should return all ingredients
        url = self.urls['ingredient_list'] + '?name='
        response = client.get(url)
        assert len(response.data) == 2


    def test_recipe_filter_by_tags(self, client, recipe, tag, tag2):
        """Test that recipe filter by tags works correctly"""
        url = (
            self.urls['recipe_list']
            + '?tags='
            + tag.slug
            + '&tags='
            + tag2.slug
        )
        response = client.get(url)
        self.assert_status_code(200, response, url=url)
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['tags'][0]['id'] == tag.id

    def test_filter_favorite_recipes(
        self, user_client, recipe, favorite, user
    ):
        """Test that favorite recipe filter works correctly"""
        url = self.urls['recipe_list'] + '?is_favorited=true'
        response = user_client.get(url)
        self.assert_status_code(200, response, url=url)
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == recipe.id

    def test_filter_recipe_in_shopping_cart(
        self, user_client, recipe, shopping_cart, user
    ):
        """Test that recipe in shopping cart filter works correctly"""
        url = self.urls['recipe_list'] + '?is_in_shopping_cart=true'
        response = user_client.get(url)
        self.assert_status_code(200, response, url=url)
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == recipe.id

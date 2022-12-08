class APITestBase:
    urls = {
        # Users
        'users': '/api/users/',
        'users_detail': '/api/users/{user_id}/',
        'users_me': '/api/users/me/',
        'set_password': '/api/users/set_password/',
        'get_token': '/api/auth/token/login/',
        'delete_token': '/api/auth/token/logout/',
        # Tags
        'tag_list': '/api/tags/',
        'tag_detail': '/api/tags/{tag_id}/',
        # Recipes
        'recipe_list': '/api/recipes/',
        'recipe_detail': '/api/recipes/{recipe_id}',
        # Shopping cart
        'shopping_cart': '/api/recipes/download_shopping_cart/',
        'recipe_in_cart': '/api/recipes/{recipe_id}/shopping_cart/',
        # Favorites
        'favorites': '/api/recipes/{recipe_id}/favorite/',
        # Subscriptions
        'subscriptions': '/api/users/subscriptions/',
        'subscribe': '/api/users/{user_id}/subscribe/',
        # Ingredients
        'ingredient_list': '/api/ingredients/',
        'ingredient_detail': '/api/ingredients/{ingredient_id}/',
    }

    def assert_fields(self, fields_required, response, *args, **kwargs):
        """Assertion to check fields in response"""
        url = kwargs.get('url')
        for field in fields_required:
            assert field in response.json().keys(), (
                f'При запросе на `{url}` должны возвращаться '
                f'{fields_required} поля. В ответе не найдено поле {field}'
            )
        return response

    def assert_status_code(self, code_expected, response, *args, **kwargs):
        """Assertion to check status code in response"""
        url = kwargs.get('url')
        response_data = ''
        try:
            response_data = response.json()
        # if no data in answer at all
        except TypeError:
            pass
        # if content-type not a json
        except ValueError:
            pass
        assert response.status_code == code_expected, (
            f'При запросе `{url}` со всеми параметрами должен возвращаться '
            f'код {code_expected}, а вернулся код {response.status_code}:'
            f' {response_data}'
        )
        return response

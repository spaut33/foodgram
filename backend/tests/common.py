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
        'add_recipe_to_cart': '/api/recipes/{recipe_id}/shopping_cart/',

        # Favorites
        'favorites': '/api/recipes/{recipe_id}/favorite/',

        # Subscriptions
        'subscriptions': '/api/users/subscriptions/',
        'subscribe': '/api/users/{user_id}/subscribe/',

        # Ingredients
        'ingredient_list': '/api/ingredients/',
        'ingredient_detail': '/api/ingredients/{ingredient_id}/'

    }
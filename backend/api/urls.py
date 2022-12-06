from django.urls import path, include
from rest_framework import routers

from api.views.recipe_views import IngredientViewSet, RecipeViewSet, TagViewSet
from api.views.shopping_cart_views import ShoppingCartViewSet
from api.views.user_views import UserViewSet, SubscriptionViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', ShoppingCartViewSet, basename='shopping_cart')
router.register('recipes', RecipeViewSet, basename='recipes')

auth = [path('auth/', include('djoser.urls.authtoken'))]

urlpatterns = [
    path('', include(auth)),
    path('', include(router.urls)),
    # Обход невозможности отключить красиво метод DELETE для joser'овского
    # ModelViewSet, подписики на юзеров сделаны отдельно более низкоуровневым
    # методом
    path(
        'users/<int:id>/subscribe/',
        SubscriptionViewSet.as_view(),
        name='user_subscriptions',
    ),
]

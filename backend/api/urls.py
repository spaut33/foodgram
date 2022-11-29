from django.urls import path, include
from rest_framework import routers

from api.views.recipe_views import IngredientViewSet, RecipeViewSet, TagViewSet
from api.views.user_views import UserViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

auth = [path('auth/', include('djoser.urls.authtoken'))]

urlpatterns = [path('', include(auth)), path('', include(router.urls))]

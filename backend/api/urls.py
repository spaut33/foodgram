from django.urls import path, include
from rest_framework import routers

from api.views.user_views import UserViewSet

app_name = 'api'
router = routers.DefaultRouter()


router.register('users', UserViewSet, basename='users')

auth = [
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('', include(auth)),
    path('', include(router.urls)),

]
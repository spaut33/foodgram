from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title='Foodgram API',
        default_version='v1',
        description='Foodgram REST API',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api'))
]

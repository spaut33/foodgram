from django.contrib.auth import get_user_model
from djoser.views import UserViewSet as DjoserUsers

User = get_user_model()


class UserViewSet(DjoserUsers):
    """Пользователи на основе Djoser."""
    
    http_method_names = ('get', 'post', 'head')

    def reset_password(self, request, *args, **kwargs):
        return None

    def activation(self, request, *args, **kwargs):
        return None

    def resend_activation(self, request, *args, **kwargs):
        return None

    def reset_username(self, request, *args, **kwargs):
        return None

    def set_username(self, request, *args, **kwargs):
        return None

    def reset_password_confirm(self, request, *args, **kwargs):
        return None

    def reset_username_confirm(self, request, *args, **kwargs):
        return None
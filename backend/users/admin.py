from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@register(User)
class UserAdmin(DjangoUserAdmin):
    readonly_fields = ('date_joined',)
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_superuser',
        'is_active',
        'date_joined',
    )
    fieldsets = (
        (None, {'fields': ('email', 'username')}),
        (
            _('Личные данные'),
            {
                'classes': ('collapse',),
                'fields': ('first_name', 'last_name', 'date_joined'),
            },
        ),
        (_('Управление'), {'fields': ('password', 'is_superuser', 'is_active')}),
    )

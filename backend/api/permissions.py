from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Администратор или суперюзер"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    """Администратор или автор записи"""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Администратор и чтение для всех юзеров"""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )

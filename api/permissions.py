from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import User


class IsAdminOrAccountOwner(BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (view.action not in ('list', 'create')
                     or request.user.role == User.Role.ADMIN))

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.role == User.Role.ADMIN


class IsAdminUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_superuser


class isAdminUserModerator(BasePermission):
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.role in (User.Role.MODERATOR, User.Role.ADMIN))

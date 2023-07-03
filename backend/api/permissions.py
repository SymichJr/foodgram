from rest_framework.permissions import DjangoModelPermissions  # noqa F401
from rest_framework.permissions import IsAuthenticated  # noqa F401
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.routers import APIRootView  # noqa F401


class BanPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
        )


class AuthorStaffOrReadOnly(BanPermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and (request.user == obj.author or request.user.is_staff)
        )


class AdminOrReadOnly(BanPermission):
    def has_object_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user.is_staff
        )


class OwnerUserOrReadOnly(BanPermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
            or request.user.is_staff
        )

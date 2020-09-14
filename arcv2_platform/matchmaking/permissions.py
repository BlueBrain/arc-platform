from rest_framework.permissions import BasePermission

from arcv2_platform.app.models import Role


class AccessSupplyAPIPermission(BasePermission):
    def has_permission(self, request, view):
        return Role.validate_roles(request.user, [Role.supplier, Role.validator, Role.moderator])


class AccessRequestAPIPermission(BasePermission):
    def has_permission(self, request, view):
        return Role.validate_roles(request.user, [Role.validator, Role.moderator])

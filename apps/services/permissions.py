from rest_framework.permissions import BasePermission


class IsCosmetologist(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "cosmetologist"
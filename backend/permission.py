from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Only allow safe methods
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
        if request.method in permissions.SAFE_METHODS:
            return True

        return False

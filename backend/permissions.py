from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Kullanıcının yalnızca kendi postunu güncellemesine veya silmesine izin verir.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

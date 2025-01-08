from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Sadece sahibi düzenleyebilir veya silebilir
        if request.method in ['PUT', 'DELETE']:
            return obj.user == request.user
        return True

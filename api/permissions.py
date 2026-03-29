from rest_framework.permissions import BasePermission, SAFE_METHODS


class EstProprietaireOuReadOnly(BasePermission):
    message = 'Vous devez être le propriétaire pour modifier cet objet.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        return getattr(obj, 'cree_par', None) == request.user


class EstAdminOuReadOnly(BasePermission):
    message = 'Seuls les administrateurs peuvent modifier cette ressource.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
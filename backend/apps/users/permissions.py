"""
Permissions personnalisées pour GeoCommerce Pro
Basées sur les rôles : Admin, Manager, Commercial
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission : uniquement les administrateurs"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsManager(permissions.BasePermission):
    """Permission : uniquement les managers"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_manager


class IsAdminOrManager(permissions.BasePermission):
    """Permission : Admin OU Manager"""

    def has_permission(self, request, view):
        return (
            request.user and request.user.is_authenticated
            and (request.user.is_admin or request.user.is_manager)
        )


class IsCommercial(permissions.BasePermission):
    """Permission : uniquement les commerciaux"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_commercial


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission : l'utilisateur ne peut accéder qu'à SES propres données,
    sauf si c'est un admin qui peut tout voir.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        # Vérifier si l'objet a un attribut 'user' ou 'commercial'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'commercial'):
            return obj.commercial.user == request.user
        return obj == request.user


class IsTeamManager(permissions.BasePermission):
    """
    Permission : un manager peut voir/modifier les données de SON ÉQUIPE.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        if request.user.is_manager:
            # Vérifier si l'objet appartient à un membre de l'équipe
            if hasattr(obj, 'user'):
                return obj.user in request.user.get_team() or obj.user == request.user
            if hasattr(obj, 'commercial'):
                return obj.commercial.user in request.user.get_team()
        return False


class RoleBasedPermission(permissions.BasePermission):
    """
    Permission dynamique basée sur le rôle de l'utilisateur.
    Admin = tout, Manager = son équipe, Commercial = ses données.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin voit tout
        if user.is_admin:
            return True

        # Commercial voit uniquement ses données
        if user.is_commercial:
            if hasattr(obj, 'user'):
                return obj.user == user
            if hasattr(obj, 'commercial'):
                return obj.commercial.user == user
            return obj == user

        # Manager voit son équipe
        if user.is_manager:
            if hasattr(obj, 'user'):
                return obj.user == user or obj.user in user.get_team()
            if hasattr(obj, 'commercial'):
                return obj.commercial.user == user or obj.commercial.user in user.get_team()
            return obj == user

        return False

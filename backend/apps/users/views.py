"""
Views pour l'authentification et la gestion des utilisateurs
"""
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, ProfileSerializer,
)
from .permissions import IsAdmin, IsAdminOrManager, IsOwnerOrAdmin, RoleBasedPermission

User = get_user_model()


class UserListView(generics.ListAPIView):
    """
    GET /api/v1/auth/users/
    Liste des utilisateurs avec recherche et filtres.
    Admin : tous. Manager : son équipe. Commercial : rien.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'manager']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['date_joined', 'last_name', 'role']
    ordering = ['-date_joined']

    def get_queryset(self):
        user = self.request.user

        if user.is_admin:
            return User.objects.all().annotate(team_count=Count('team_members'))

        if user.is_manager:
            # Le manager voit lui-même + son équipe
            return User.objects.filter(
                Q(id=user.id) | Q(manager=user)
            ).annotate(team_count=Count('team_members'))

        return User.objects.none()


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE /api/v1/auth/users/<id>/
    Détail, modification, suppression d'un utilisateur.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrManager]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return User.objects.all()
        if user.is_manager:
            return User.objects.filter(Q(id=user.id) | Q(manager=user))
        return User.objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer

    def perform_destroy(self, instance):
        """Soft delete : désactiver au lieu de supprimer"""
        instance.is_active = False
        instance.save()


class UserCreateView(generics.CreateAPIView):
    """
    POST /api/v1/auth/users/
    Création d'un nouvel utilisateur (Admin/Manager uniquement)
    """
    serializer_class = UserCreateSerializer
    permission_classes = [IsAdminOrManager]


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT /api/v1/auth/profile/
    Profil de l'utilisateur connecté
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """
    POST /api/v1/auth/change-password/
    Changement de mot de passe
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        # Invalider tous les refresh tokens (déconnexion de tous les appareils)
        RefreshToken.for_user(user)

        return Response({
            'success': True,
            'message': 'Mot de passe modifié avec succès. Veuillez vous reconnecter.'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST /api/v1/auth/logout/
    Déconnexion sécurisée : blacklist le refresh token
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'success': False,
                'error': 'Le token refresh est requis.'
            }, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({
            'success': True,
            'message': 'Déconnexion réussie.'
        }, status=status.HTTP_205_RESET_CONTENT)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all_view(request):
    """
    POST /api/v1/auth/logout-all/
    Déconnexion de TOUS les appareils
    """
    try:
        # Blacklister tous les refresh tokens de l'utilisateur
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        tokens = OutstandingToken.objects.filter(user=request.user)
        for token in tokens:
            token.blacklistedtoken_set.get_or_create()

        return Response({
            'success': True,
            'message': 'Toutes les sessions ont été terminées.'
        }, status=status.HTTP_205_RESET_CONTENT)

    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    GET /api/v1/auth/me/
    Informations de l'utilisateur connecté (pour le frontend au chargement)
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response({
        'success': True,
        'user': serializer.data
    })

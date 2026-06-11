"""
Serializers pour l'authentification et la gestion des utilisateurs
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer JWT personnalisé avec connexion par email
    """
    
    def validate(self, attrs):
        email = attrs.get('email')
        if email:
            attrs['username'] = email
        
        data = super().validate(attrs)
        
        # Ajouter les données utilisateur dans la réponse
        user = self.user
        photo_url = None
        if user.photo and hasattr(user.photo, 'url'):
            photo_url = user.photo.url
        
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'photo': photo_url,
        }
        
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        return token


class UserSerializer(serializers.ModelSerializer):
    """Serializer de base pour les utilisateurs"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    team_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'role', 'role_display', 'phone', 'photo',
            'is_active', 'manager', 'team_count',
            'date_joined', 'last_modified',
        ]
        read_only_fields = ['id', 'date_joined', 'last_modified']

    def get_team_count(self, obj):
        if obj.is_manager:
            return obj.team_members.filter(is_active=True).count()
        return 0

    def validate_email(self, value):
        """Vérifier l'unicité de l'email (insensible à la casse)"""
        value = value.lower().strip()
        if User.objects.filter(email=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_phone(self, value):
        """Validation format téléphone international"""
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                "Le numéro doit inclure l'indicatif international (ex: +237...)"
            )
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'utilisateur avec mot de passe"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'phone', 'photo', 'password', 'password_confirm',
            'manager',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError(
                {'password_confirm': "Les mots de passe ne correspondent pas."}
            )

        # Vérifier que le manager a bien le rôle MANAGER
        manager = attrs.get('manager')
        if manager and not manager.is_manager:
            raise serializers.ValidationError(
                {'manager': "L'utilisateur sélectionné n'est pas un manager."}
            )

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'utilisateur"""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'photo',
            'role', 'manager', 'is_active',
        ]

    def validate_role(self, value):
        """Empêcher un commercial de devenir admin"""
        request = self.context.get('request')
        if request and not request.user.is_admin:
            raise serializers.ValidationError(
                "Vous n'avez pas les droits pour modifier le rôle."
            )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, validators=[validate_password], style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': "Les mots de passe ne correspondent pas."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil de l'utilisateur connecté"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'photo', 'role', 'date_joined',
        ]
        read_only_fields = ['id', 'email', 'role', 'date_joined']
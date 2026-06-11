"""
Serializers pour l'authentification et la gestion des utilisateurs
"""
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer JWT avec connexion par EMAIL
    """
    username_field = 'email'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
        self.fields['email'] = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                {'non_field_errors': 'Email et mot de passe requis.'}
            )

        self.user = authenticate(
              request=self.context.get('request'),
              username=email.lower().strip(),  # ← On passe l'email comme username
              password=password
        )

        if self.user is None:
            raise serializers.ValidationError(
                {'email': 'Email ou mot de passe incorrect.'}
            )

        if not self.user.is_active:
            raise serializers.ValidationError(
                {'email': 'Ce compte est desactive.'}
            )

        data = {}
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'role': self.user.role,
            'photo': self.user.photo.url if self.user.photo else None,
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
        value = value.lower().strip()
        if User.objects.filter(email=value).exclude(
            id=self.instance.id if self.instance else None
        ).exists():
            raise serializers.ValidationError("Cet email est deja utilise.")
        return value

    def validate_phone(self, value):
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                "Le numero doit inclure l'indicatif international (ex: +237...)"
            )
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'phone', 'photo', 'password', 'password_confirm', 'manager',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError(
                {'password_confirm': "Les mots de passe ne correspondent pas."}
            )
        manager = attrs.get('manager')
        if manager and not manager.is_manager:
            raise serializers.ValidationError(
                {'manager': "L'utilisateur selectionne n'est pas un manager."}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'photo', 'role', 'manager', 'is_active']

    def validate_role(self, value):
        request = self.context.get('request')
        if request and not request.user.is_admin:
            raise serializers.ValidationError(
                "Vous n'avez pas les droits pour modifier le role."
            )
        return value


class ChangePasswordSerializer(serializers.Serializer):
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
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'photo', 'role', 'date_joined',
        ]
        read_only_fields = ['id', 'email', 'role', 'date_joined']
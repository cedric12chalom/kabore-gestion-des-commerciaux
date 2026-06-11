"""
Authentication backend for email-based login
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows login with email instead of username.
    """
    
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        if email is None:
            email = username
        if email is None or password is None:
            return None
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        
        if user.check_password(password) and user.is_active:
            return user
        return None
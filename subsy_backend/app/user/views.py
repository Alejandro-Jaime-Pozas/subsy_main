"""
Views for the User api.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from core.views import BaseAuthPermissions
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the db."""
    serializer_class = UserSerializer
    permission_classes = []


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer


class ManageUserView(BaseAuthPermissions, generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user

"""
Views for the User api.
"""
from rest_framework import generics
from rest_framework.permissions import AllowAny

from user.serializers import UserSerializer
from django.contrib.auth import get_user_model


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer
    permission_classes = []  # Allow any user to access this view req for test APIClient to work, will need to remove this later

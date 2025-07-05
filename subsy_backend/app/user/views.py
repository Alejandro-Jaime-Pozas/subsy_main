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
    """Create a new auth token for user and set it as HttpOnly cookie."""
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        # Call the parent class's post method to handle authentication and token creation
        response = super().post(request, *args, **kwargs)

        # Get the token from the response
        token = response.data.get('token')

        if token:
            # Set the token as an HttpOnly cookie
            response.set_cookie(
                key='auth_token',
                value=token,
                httponly=True,
                secure=False,  # TODO Set to True in production (requires HTTPS)
                samesite='Lax',
                max_age=60*60*24*7,  # 1 week
            )

            # Optionally, remove the token from the response body for security
            # response.data.pop('token', None)  # TODO INCLUDE FOR PROD

        return response


class ManageUserView(BaseAuthPermissions, generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user

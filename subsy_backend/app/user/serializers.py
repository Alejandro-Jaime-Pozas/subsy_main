"""
Serializers for the user API view.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
        ]  # only allow fields that the user will be able to change, no admin only fields
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}  # user will only be able to write to pwd, they cannot read the pwd

    # overwrite the create method to call our custom user model (which removes pwd)
    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

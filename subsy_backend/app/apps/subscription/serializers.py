from rest_framework import serializers

from core.models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Subscription model.
    """

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = [field.name for field in model._meta.fields]

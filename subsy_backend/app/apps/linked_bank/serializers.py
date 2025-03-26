from rest_framework import serializers

from core.models import LinkedBank


class LinkedBankSerializer(serializers.ModelSerializer):
    """
    Serializer for the LinkedBank model.
    """

    class Meta:
        model = LinkedBank
        fields = '__all__'
        read_only_fields = [field.name for field in model._meta.fields]

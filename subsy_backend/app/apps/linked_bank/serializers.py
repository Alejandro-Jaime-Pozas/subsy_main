from rest_framework.serializers import ModelSerializer

from core.models import LinkedBank


class LinkedBankSerializer(ModelSerializer):
    """
    Serializer for the LinkedBank model.
    """

    class Meta:
        model = LinkedBank
        fields = '__all__'
        read_only_fields = [field.name for field in model._meta.fields]

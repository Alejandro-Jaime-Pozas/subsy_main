from rest_framework import serializers

from core.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model.
    """

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = [field.name for field in model._meta.fields]

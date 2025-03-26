from rest_framework import serializers
from core.models import BankAccount


class BankAccountSerializer(serializers.ModelSerializer):
    """Serializer for the bank account objects."""

    class Meta:
        model = BankAccount
        fields = '__all__'
        read_only_fields = [field.name for field in BankAccount._meta.fields]

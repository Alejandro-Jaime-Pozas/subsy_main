from rest_framework import serializers

from core.models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Application model.
    """

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = [field.name for field in model._meta.fields]

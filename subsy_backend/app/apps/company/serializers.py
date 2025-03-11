from rest_framework import serializers

from core.models import Company


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ['id']

# will perhaps later need to modify companies to return just for the user? not sure

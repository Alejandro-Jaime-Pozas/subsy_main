from rest_framework import serializers

from core.models import LinkedBank


class LinkedBankSerializer(serializers.ModelSerializer):
    """
    Serializer for the LinkedBank model.
    Excludes sensitive fields (access_token, cursor) from serialized data.
    """

    class Meta:
        model = LinkedBank
        exclude = ['access_token', 'cursor']
        read_only_fields = [field.name for field in model._meta.fields]

        # Other possible Meta options:
        # fields = ['id', 'item_id', 'institution_id', 'institution_name', 'company']
        # exclude = ['access_token', 'cursor']  # Alternative to specifying fields
        # depth = 1  # How deep to serialize nested relationships
        # extra_kwargs = {
        #     'field_name': {
        #         'write_only': True,      # Only for input
        #         'read_only': True,       # Only for output
        #         'required': False,       # Optional field
        #         'default': 'value',      # Default value
        #         'allow_null': True,      # Allow null values
        #         'allow_blank': True,     # Allow empty strings
        #         'min_length': 3,         # Minimum length
        #         'max_length': 100,       # Maximum length
        #     }
        # }
        # validators = [UniqueTogetherValidator(...)]  # Custom validators
        # list_serializer_class = CustomListSerializer  # Custom list serializer

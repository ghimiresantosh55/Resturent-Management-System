from rest_framework import serializers
from .models import Customer
from django.utils import timezone
from utils.functions import current_user
from rest_framework import serializers
from .models import Table, Block


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        block = Block.objects.create(**validated_data, created_date_ad=timezone.now())
        return block


class TableSerializer(serializers.ModelSerializer):
    block_name = serializers.ReadOnlyField(source='block.name')
    block_display_order = serializers.ReadOnlyField(source='block.display_order')
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)

    class Meta:
        model = Table
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        validated_data['created_by'] = current_user.get_created_by(self.context)
        table = Table.objects.create(**validated_data, created_date_ad=timezone.now())
        return table

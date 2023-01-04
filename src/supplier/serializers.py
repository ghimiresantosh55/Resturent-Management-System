from rest_framework import serializers
from utils.functions import current_user
from django.utils import timezone
# imported model here
from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        supplier = Supplier.objects.create(**validated_data, created_date_ad=date_now)
        return supplier

    def to_representation(self, instance):
        my_fields = {'image'}
        data = super().to_representation(instance)
        for field in my_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data

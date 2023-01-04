from rest_framework.serializers import ModelSerializer
from .models import UserGroup, UserPermission, UserPermissionCategory
from django.utils import timezone
from utils.functions import current_user


class CustomGroupSerializer(ModelSerializer):
    class Meta:
        model = UserGroup
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        permissions = validated_data.pop('permissions')
        validated_data['created_by'] = current_user.get_created_by(self.context)
        instance = UserGroup.objects.create(**validated_data, created_date_ad=date_now)
        for permission in permissions:
            instance.permissions.add(permission)
        return instance


class CustomPermissionSerializer(ModelSerializer):
    class Meta:
        model = UserPermission
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        instance = UserPermission.objects.create(**validated_data, created_date_ad=date_now)
        return instance


class PermissionCategorySerializer(ModelSerializer):
    class Meta:
        model = UserPermissionCategory
        fields = '__all__'
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        instance = UserPermissionCategory.objects.create(**validated_data, created_date_ad=date_now)
        return instance

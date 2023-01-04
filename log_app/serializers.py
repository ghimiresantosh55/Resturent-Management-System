from rest_framework import serializers
from .models import UserAccessLog


class UserLoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccessLog
        fields = "__all__"

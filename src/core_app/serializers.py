from django.db import models
from rest_framework import serializers

from .models import OrganizationRule, OrganizationSetup, Country, Province, District, AppAccessLog
from .models import Bank, BankDeposit, PaymentMode, DiscountScheme, AdditionalChargeType
from utils.functions import current_user
from django.utils import timezone


class CountrySerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)

    class Meta:
        model = Country
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        instance = Country.objects.create(**validated_data, created_date_ad=date_now)
        return instance


class ProvinceSerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)

    class Meta:
        model = Province
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        instance = Province.objects.create(**validated_data, created_date_ad=date_now)
        return instance


class DistrictSerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)
    province_name = serializers.ReadOnlyField(source='province.name', allow_null=True)

    class Meta:
        model = District
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        instance = District.objects.create(**validated_data, created_date_ad=date_now)
        return instance


class OrganizationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationRule
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        organization_rule = OrganizationRule.objects.create(**validated_data, created_date_ad=date_now)
        return organization_rule


class OrganizationSetupSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationSetup
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        organization_setup = OrganizationSetup.objects.create(**validated_data, created_date_ad=date_now)
        return organization_setup


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        bank = Bank.objects.create(**validated_data, created_date_ad=date_now)
        return bank


class BankDepositSerializer(serializers.ModelSerializer):
    bank_name = serializers.ReadOnlyField(source='bank.name', allow_null=True)

    class Meta:
        model = BankDeposit
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        bank_deposit = BankDeposit.objects.create(**validated_data, created_date_ad=date_now)
        return bank_deposit


class PaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        payment_mode = PaymentMode.objects.create(**validated_data, created_date_ad=date_now)
        return payment_mode


class DiscountSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountScheme
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        discount_scheme = DiscountScheme.objects.create(**validated_data, created_date_ad=date_now)
        return discount_scheme


class AdditionalChargeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalChargeType
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        charge_type = AdditionalChargeType.objects.create(**validated_data, created_date_ad=date_now)
        return charge_type


class AppAccessLogSerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)
    device_type_display = serializers.ReadOnlyField(source="get_device_type_display", allow_null=True)
    app_type_display = serializers.ReadOnlyField(source="get_app_type_display", allow_null=True)

    class Meta:
        model = AppAccessLog
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        date_now = timezone.now()
        validated_data['created_by'] = current_user.get_created_by(self.context)
        app_access_log = AppAccessLog.objects.create(**validated_data, created_date_ad=date_now)
        return app_access_log

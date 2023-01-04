from re import T
from rest_framework import serializers
from src.credit_management.models import CreditClearance, CreditPaymentDetail
from utils.functions.current_user import get_created_by
from src.sale.models import SaleMain
from django.utils import timezone


class CreditPaymentMainSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    sale_no = serializers.ReadOnlyField(source='sale_main.sale_no', allow_null=True)
    payment_type_display=serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)
    class Meta:
        model = CreditClearance
        fields = "__all__"
        read_only_fields=['payment_type_display']


class CreditPaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPaymentDetail
        fields = '__all__'
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


"""_________________________________save credit payment details_________________________________________________"""


class SaveCreditPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name')

    class Meta:
        model = CreditPaymentDetail
        exclude = ['credit_clearance']
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


class SaveCreditClearanceSerializer(serializers.ModelSerializer):
    credit_payment_details = SaveCreditPaymentDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)
    sale_no = serializers.ReadOnlyField(source='sale_main.sale_no', allow_null=True)

    class Meta:
        model = CreditClearance
        fields = "__all__"
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')

    def create(self, validated_data):
        date_now = timezone.now()
        credit_payment_details = validated_data.pop('credit_payment_details')

        validated_data['created_by'] = get_created_by(self.context)

        credit_clearance = CreditClearance.objects.create(**validated_data, created_date_ad=date_now)
        for credit_payment_detail in credit_payment_details:
            CreditPaymentDetail.objects.create(**credit_payment_detail, credit_clearance=credit_clearance,
                                               created_by=validated_data['created_by'], created_date_ad=date_now)

        return credit_clearance


"""_______________________ serializer for Credit Sale Report _______________________________________________"""


class SaleCreditSerializer(serializers.ModelSerializer):
    sale_id = serializers.ReadOnlyField(source='id')
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    total_amount = serializers.ReadOnlyField(source='grand_total')
    paid_amount = serializers.SerializerMethodField()
    due_amount = serializers.SerializerMethodField()

    class Meta:
        model = SaleMain
        fields = ['sale_id', 'sale_no', 'customer', 'customer_first_name', 'customer_middle_name',
                  'customer_last_name', 'total_amount',
                  'paid_amount', 'due_amount', 'created_date_ad', 'created_date_bs',
                  'created_by', 'created_by_user_name', 'remarks']

    def get_paid_amount(self, instance):
        paid_amount = sum(CreditClearance.objects.filter(sale_main=instance.id)
                          .values_list('total_amount', flat=True))
        return paid_amount

    def get_due_amount(self, instance):
        paid_amount = self.get_paid_amount(instance)
        due_amount = instance.grand_total - paid_amount
        return due_amount


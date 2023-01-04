from rest_framework import serializers, status
from .models import OrderMain
from utils.functions import current_user
from django.utils import timezone
from decimal import Decimal
from src.advance_deposit.models import AdvanceDeposit, AdvanceDepositPaymentDetail
from .advance_deposit_unique_id_generator import generate_advance_deposit_no



class AdvanceDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceDeposit
        fields = "__all__"


class AdvanceDepositPaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvanceDepositPaymentDetail
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveAdvanceDepositPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = AdvanceDepositPaymentDetail
        exclude = ["advance_deposit"]
        read_only_fields = ['payment_mode_name', 'created_date_ad', 'created_date_bs', 'created_by']


class SaveAdvanceDepositSerializer(serializers.ModelSerializer):
    advance_deposit_payment_details = SaveAdvanceDepositPaymentDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)

    class Meta:
        model = AdvanceDeposit
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by', 'deposit_no']

    def create(self, validated_data):
        date_now = timezone.now()
        payment_details = validated_data.pop('advance_deposit_payment_details')
        if not payment_details:
            raise serializers.ValidationError("Please provide at least one payment detail")

        validated_data['created_by'] = current_user.get_created_by(self.context)
        validated_data['deposit_no'] = generate_advance_deposit_no()
        advance_deposit = AdvanceDeposit.objects.create(**validated_data, created_date_ad=date_now)

        for detail in payment_details:
            AdvanceDepositPaymentDetail.objects.create(**detail, advance_deposit=advance_deposit,
                                                       created_by=validated_data['created_by'],
                                                       created_date_ad=date_now)
        return advance_deposit

    def validate(self, data):
        order_main = data['order_main']
        advance_payment_amount = data['amount']
        # raise serializers.ValidationError({'amount_no_valid':'Advance deposit must not be greater than total_amount'})

        order_amount = OrderMain.objects.get(id=order_main.id).grand_total
        older_advance_payments = sum(AdvanceDeposit.objects.filter(order_main=order_main.id).values_list('amount', flat=True))
        advance_payment_amount += older_advance_payments
        if order_amount < advance_payment_amount:
            raise serializers.ValidationError({'amount_no_valid': 'Advance deposit must not be greater than total_amount'})

        payment_details = data['advance_deposit_payment_details']
        total_amount = Decimal('0.00')
        for payment in payment_details:
            total_amount += payment['amount']
        if total_amount != data['amount']:
            raise serializers.ValidationError('Advance deposit amount not equal to'
                                              ' advance_deposit_payment_detail amount')

        return data

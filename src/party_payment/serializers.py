from rest_framework import serializers
from src.party_payment.models import PartyClearance, PartyPaymentDetail
from utils.functions.current_user import get_created_by
from src.purchase.models import PurchaseMain
from django.utils import timezone


class PartyClearanceMainSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)
    purchase_no = serializers.ReadOnlyField(source='purchase_main.purchase_no', allow_null=True)

    class Meta:
        model = PartyClearance
        fields = "__all__"


class PartyPaymentDetailSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = PartyPaymentDetail
        fields = '__all__'
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


"""_________________________________save credit payment details_________________________________________________"""


class SavePartyPaymentDetailSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name')

    class Meta:
        model = PartyPaymentDetail
        exclude = ['party_clearance']
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


class SavePartyClearanceSerializer(serializers.ModelSerializer):
    party_payment_details = SavePartyPaymentDetailSerializer(many=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    purchase_no = serializers.ReadOnlyField(source='purchase_main.purchase_no', allow_null=True)
    payment_type_display = serializers.ReadOnlyField(source='get_payment_type_display', allow_null=True)

    class Meta:
        model = PartyClearance
        fields = "__all__"
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')

    def create(self, validated_data):
        date_now = timezone.now()
        party_payment_details = validated_data.pop('party_payment_details')

        validated_data['created_by'] = get_created_by(self.context)

        party_clearance = PartyClearance.objects.create(**validated_data, created_date_ad=date_now)
        for party_payment_detail in party_payment_details:
            PartyPaymentDetail.objects.create(**party_payment_detail, party_clearance=party_clearance,
                                              created_by=validated_data['created_by'], created_date_ad=date_now)

        return party_clearance


"""_______________________ serializer for Credit Sale Report _______________________________________________"""


class PurchaseCreditSerializer(serializers.ModelSerializer):
    purchase_id = serializers.ReadOnlyField(source='id')
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_middle_name = serializers.ReadOnlyField(source='customer.middle_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    total_amount = serializers.ReadOnlyField(source='grand_total')
    paid_amount = serializers.SerializerMethodField()
    due_amount = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseMain
        fields = ['purchase_id', 'created_by_user_name', 'customer_first_name', 'customer_middle_name',
                  'customer_last_name', 'total_amount',
                  'paid_amount', 'due_amount', 'purchase_no', 'supplier', 'created_date_ad', 'created_date_bs',
                  'created_by', 'remarks']

    def get_paid_amount(self, instance):
        paid_amount = sum(PartyClearance.objects.filter(purchase_main=instance.id)
                          .values_list('total_amount', flat=True))
        return paid_amount

    def get_due_amount(self, instance):
        paid_amount = self.get_paid_amount(instance)
        due_amount = instance.grand_total - paid_amount
        return due_amount

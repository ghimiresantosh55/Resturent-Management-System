from django.db import models
from django.db.models import fields
from rest_framework import serializers
from rest_framework.utils import field_mapping
from .models import SaleMain, SaleDetail, SalePaymentDetail, SalePrintLog
from decimal import Decimal
from django.utils import timezone
from utils.functions.current_user import get_created_by
from utils.functions.stock import get_sale_return_qty, get_sale_remaining_qty
from src.credit_management.reciept_unique_id_generator import get_receipt_no
from src.credit_management.models import CreditClearance, CreditPaymentDetail
from .models import SaleAdditionalCharge
from src.customer_order.models import OrderMain
from src.advance_deposit.models import AdvanceDeposit

# to update customer order main on sale
class UpdateCustomerOrderMsterSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderMain
        fields = '__all__'


# For Read only View
class SaleMainSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    sale_type_display = serializers.ReadOnlyField(source='get_sale_type_display', allow_null=True)
    pay_type_display = serializers.ReadOnlyField(source='get_pay_type_display', allow_null=True)

    class Meta:
        model = SaleMain
        fields = "__all__"
        read_only_fields = ['sale_type_display','pay_type_display','created_by','created_date_ad', 'created_date_bs']


# For read only View
class SaleDetailSerializer(serializers.ModelSerializer):
    sale_no = serializers.ReadOnlyField(source='sale_main.sale_no')
    item_name = serializers.ReadOnlyField(source='item.name')
    item_category_name = serializers.ReadOnlyField(source='item_category.name')

    class Meta:
        model = SaleDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# For read only view
class SaleAdditionalChargeSerializer(serializers.ModelSerializer):
    charge_type_name = serializers.ReadOnlyField(source='charge_type.name', allow_null=True)

    class Meta:
        model = SaleAdditionalCharge
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# For read only view
class SalePaymentDetailSerializer(serializers.ModelSerializer):
    sale_no = serializers.ReadOnlyField(source='sale_main.sale_no', allow_null=True)
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = SalePaymentDetail
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


class SaleDetailForSaleReturnSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    item_category_name = serializers.ReadOnlyField(source='item_category.name')
    expiry_date_ad = serializers.ReadOnlyField(source='ref_purchase_detail.expiry_date_ad')
    expiry_date_bs = serializers.ReadOnlyField(source='ref_purchase_detail.expiry_date_bs')
    location = serializers.ReadOnlyField(source='item.location')
    batch_no = serializers.ReadOnlyField(source='ref_purchase_detail.batch_no')
    return_qty = serializers.SerializerMethodField()
    remaining_qty = serializers.SerializerMethodField()

    class Meta:
        model = SaleDetail
        exclude = ['created_date_ad', 'created_date_bs', 'ref_sale_detail', 'created_by']

    def get_return_qty(self, sale):
        sale_id = sale.id
        qty = get_sale_return_qty(sale_id)
        return qty

    def get_remaining_qty(self, sale):
        sale_id = sale.id
        qty = get_sale_remaining_qty(sale_id)
        return qty


# For Read and Write View
class SaveSaleDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    item_category_name = serializers.ReadOnlyField(source='item_category.name', allow_null=True)
    sale_no = serializers.ReadOnlyField(source='sale_main.sale_no')

    class Meta:
        model = SaleDetail
        exclude = ['sale_main']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# For Read and Write View
class SaveSalePaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePaymentDetail
        exclude = ['sale_main']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# for Write
class SaveSaleAdditionalCharge(serializers.ModelSerializer):
    class Meta:
        model = SaleAdditionalCharge
        exclude = ['sale_main']
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']


# For Read and Write View
class SaveSaleMainSerializer(serializers.ModelSerializer):
    sale_details = SaveSaleDetailSerializer(many=True)
    payment_details = SaveSalePaymentDetailSerializer(many=True)
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name')
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name')
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name')
    sale_additional_charges = SaveSaleAdditionalCharge(many=True)

    class Meta:
        model = SaleMain
        fields = "__all__"
        read_only_fields = ['created_by', 'created_date_ad', 'created_date_bs']

    def create(self, validated_data):
        quantize_places = Decimal(10) ** -2

        validated_data['created_by'] = get_created_by(self.context)
        date_now = timezone.now()
        sale_details = validated_data.pop('sale_details')
        if not sale_details:
            serializers.ValidationError("Please provide at least one sale detail")

        payment_details = validated_data.pop('payment_details')
        additional_charges = validated_data.pop('sale_additional_charges')

        if not payment_details:
            serializers.ValidationError("Please provide payment details")
        sale_main = SaleMain.objects.create(**validated_data, created_date_ad=date_now)
        for sale_detail in sale_details:
            SaleDetail.objects.create(**sale_detail, sale_main=sale_main, created_by=validated_data['created_by'],
                                      created_date_ad=date_now)

        for additional_charge in additional_charges:
            SaleAdditionalCharge.objects.create(**additional_charge, sale_main=sale_main, created_by=validated_data['created_by'],
                                                created_date_ad=date_now)

        """________________________calculation for  payment ______________________________________"""
        # Payment detail for CASH payment
        if validated_data['pay_type'] == 1:
            # all payment details are stored in PaymentDetails Model
            for payment_detail in payment_details:
                SalePaymentDetail.objects.create(
                    **payment_detail, sale_main=sale_main,
                    created_by=validated_data['created_by'], created_date_ad=date_now
                )
            return sale_main

        # Payment Detail for CREDIT payment
        elif validated_data['pay_type'] == 2:
            # calculating total amount
            total_amount = Decimal('0.00')
            for detail in payment_details:
                amount = Decimal(str(detail['amount']))
                total_amount = total_amount + amount
            total_amount = total_amount.quantize(quantize_places)
            # 1. save Credit payment Main,
            credit_clearance_main_data = {
                'payment_type': 1,
                'sale_main': sale_main,
                'receipt_no': get_receipt_no(),
                'total_amount': total_amount,
                'remarks': validated_data['remarks'],
                'created_by': validated_data['created_by']
            }
            credit_clearance_main = CreditClearance.objects.create(**credit_clearance_main_data,
                                                                   created_date_ad=date_now)

            # 2. save Credit Payment Model Detail
            for payment_detail in payment_details:
                CreditPaymentDetail.objects.create(
                    **payment_detail,
                    credit_clearance=credit_clearance_main,
                    created_by=validated_data['created_by'], created_date_ad=date_now
                )
            return sale_main

    def validate(self, data):
        quantize_places = Decimal(10) ** -2
        # initialize variables to check
        sub_total = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_discountable_amount = Decimal('0.00')
        total_taxable_amount = Decimal('0.00')
        total_nontaxable_amount = Decimal('0.00')
        total_tax = Decimal('0.00')
        grand_total = Decimal('0.00')
        sale_details = data['sale_details']

        for sale in sale_details:
            sale_detail = {}
            key_values = zip(sale.keys(), sale.values())
            for key, values in key_values:
                sale_detail[key] = values

            # validation for amount values less than or equal to 0 "Zero"
            if sale_detail['tax_rate'] < 0 or sale_detail['discount_rate'] < 0 or \
                    sale_detail['cost'] < 0 or sale_detail['discount_amount'] < 0 or sale_detail['tax_amount'] < 0 or \
                    sale_detail['gross_amount'] < 0 or sale_detail['net_amount'] < 0:
                raise serializers.ValidationError({
                    f'item {sale_detail["item"].name}': 'values in fields of amount and rates cannot be less than 0'})
            if sale_detail['cost'] <= 0 or sale_detail['qty'] <= 0:
                raise serializers.ValidationError({
                    f'item {sale_detail["item"].name}': 'values in fields, cost and quantity cannot be less than'
                                                        ' or equals to 0'})
            if sale_detail['discount_rate'] > 100:
                raise serializers.ValidationError(
                    {f'item {sale_detail["item"].name}': 'Discount rate can not be greater than 100.'})

            # validation for gross_amount
            gross_amount = sale_detail['cost'] * sale_detail['qty']
            gross_amount = gross_amount.quantize(quantize_places)
            if gross_amount != sale_detail['gross_amount']:
                raise serializers.ValidationError(
                    {f'item {sale_detail["item"].name}': f'gross_amount calculation not valid : should be {gross_amount}'})
            sub_total = sub_total + gross_amount

            # validation for discount amount
            if sale_detail['discountable'] is True:
                total_discountable_amount = total_discountable_amount + sale_detail['gross_amount']
                discount_rate = (sale_detail['discount_amount'] *
                                 Decimal('100')) / (sale_detail['cost'] *
                                                    sale_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                if discount_rate != sale_detail['discount_rate']:
                    raise serializers.ValidationError(
                        {
                            f'item {sale_detail["item"].name}': f'discount_rate calculation not valid : '
                                                                f'should be {discount_rate}'})
                total_discount = total_discount + sale_detail['discount_amount']
            elif sale_detail['discountable'] is False and sale_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {sale_detail["item"].name}':
                    f'discount_amount {sale_detail["discount_amount"]} can not be '
                    f'given to item with discountable = False'})

            # validation for tax amount
            probable_taxable_amount = gross_amount - sale_detail["discount_amount"]
            if sale_detail['taxable'] is True:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = sale_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != sale_detail['tax_amount']:
                    raise serializers.ValidationError({f'item {sale_detail["item"].name}':
                        f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif sale_detail['taxable'] is False:
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((sale_detail['cost'] *
                                           sale_detail['qty'] *
                                           sale_detail['discount_rate']) / Decimal('100'))) + \
                         ((gross_amount - (sale_detail['cost'] *
                                           sale_detail['qty'] *
                                           sale_detail['discount_rate']) / Decimal('100')) *
                          sale_detail['tax_rate'] / Decimal('100'))
            net_amount = net_amount.quantize(quantize_places)
            if net_amount != sale_detail['net_amount']:
                raise serializers.ValidationError({f'item {sale_detail["item"].name}':
                    f'net_amount calculation not valid : should be {net_amount}'})
            grand_total = grand_total + net_amount

        # Validation for Customer_order Advanced_payment
        total_advanced_payment = Decimal('0.00')
        if data['ref_order_main'] is not None:
            order_main = data['ref_order_main']
            order_main_id = order_main.id
            total_advanced_payment = sum(AdvanceDeposit.objects.filter(order_main=order_main_id).values_list('amount', flat=True))

        # validation for purchase in CREDIT with no supplier
        if data['pay_type'] == 2 and data['customer'] == '':
            return serializers.ValidationError('Cannot perform sale in CREDIT with no Customer')

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                'total_discountable_amount calculation {} not valid: should be {}'.format(
                    data['total_discountable_amount'], total_discountable_amount)
            )

        # validation for total_taxable_amount
        if total_taxable_amount != data['total_taxable_amount']:
            raise serializers.ValidationError(
                'total_taxable_amount calculation {} not valid: should be {}'.format(data['total_taxable_amount'],
                                                                                     total_taxable_amount)
            )

        # validation for total_non_taxable_amount
        if total_nontaxable_amount != data['total_non_taxable_amount']:
            raise serializers.ValidationError(
                'total_non_taxable_amount calculation {} not valid: should be {}'.format(
                    data['total_non_taxable_amount'],
                    total_nontaxable_amount)
            )
        # # calculating additional charge
        try:
            data['sale_additional_charges']
        except KeyError:
            raise serializers.ValidationError(
                {'sale_additional_charges': 'Provide sale_additional_charges key'}
            )
        sale_additional_charges = data['sale_additional_charges']
        add_charge = Decimal('0.00')
        for sale_additional_charge in sale_additional_charges:
            add_charge = add_charge + sale_additional_charge['amount']
        grand_total += add_charge

        # check subtotal , total discount , total tax and grand total
        if sub_total != data['sub_total']:
            raise serializers.ValidationError(
                'sub_total calculation not valid: should be {}'.format(sub_total)
            )
        if total_discount != data['total_discount']:
            raise serializers.ValidationError(
                'total_discount calculation {} not valid: should be {}'.format(data['total_discount'], total_discount)
            )
        if total_tax != data['total_tax']:
            raise serializers.ValidationError(
                'total_tax calculation {} not valid: should be {}'.format(data['total_tax'], total_tax)
            )
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                'grand_total calculation {} not valid: should be {}'.format(data['grand_total'], grand_total)
            )

        # validation of payment details
        try:
            data['payment_details']
        except KeyError:
            raise serializers.ValidationError(
                {'payment_details': 'Provide payment details'}
            )
        try:
            data['pay_type']
        except KeyError:
            raise serializers.ValidationError(
                {'pay_type': 'please provide pay_type key'}
            )
        payment_details = data['payment_details']
        total_payment = Decimal('0.00')

        for payment_detail in payment_details:
            total_payment = total_payment + Decimal(str(payment_detail['amount']))
        # adding advanced payment to total payment 
        total_payment += total_advanced_payment
        # if Pay_type = CASH
        if data['pay_type'] == 1:
            if total_payment != data['grand_total']:
                raise serializers.ValidationError(
                    {'amount': 'sum of amount {} should be equal to grand_total {} in pay_type CASH'.format(
                        total_payment, data['grand_total'])}
                )
        # if pay_type = CREDIT
        elif data['pay_type'] == 2 and data['sale_type'] == 1:
            if total_payment >= data['grand_total']:
                raise serializers.ValidationError(
                    {
                        'amount': 'Cannot process sale CREDIT with total paid amount greater than or equal to{}'.format(
                            data['grand_total'])}
                )
        return data


class SalePrintLogSerializer(serializers.ModelSerializer):
    created_by_first_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_middle_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_last_name = serializers.ReadOnlyField(source="created_by.first_name", allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source="created_by.user_name", allow_null=True)
    sale_main_sale_no = serializers.ReadOnlyField(source="sale_main.sale_no", allow_null=True)

    class Meta:
        model = SalePrintLog
        fields = "__all__"
        read_only_fields = ['sale_main_sale_no']
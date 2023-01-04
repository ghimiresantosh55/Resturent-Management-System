from django.db import models
from rest_framework import serializers, status
from src.sale.models import SaleMain
from .models import OrderMain, OrderDetail
from src.item.models import Item
from django.core.exceptions import ValidationError
from utils.functions import current_user
from django.utils import timezone
from decimal import Decimal
from src.rims_setup.models import Table
from src.advance_deposit.models import AdvanceDeposit, AdvanceDepositPaymentDetail

# Used for Cancel order
class OrderMainSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)

    class Meta:
        model = OrderMain
        fields = '__all__'
        read_only_fields = ['status_display', 'created_date_ad', 'created_date_bs', 'created_by']


# used for cancel order
class OrderDetailSerializer(serializers.ModelSerializer):
    order_no = serializers.ReadOnlyField(source='order.order_no', allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(
        source='created_by.user_name', allow_null=True
    )

    class Meta:
        model = OrderDetail
        fields = '__all__'
        read_only_fields = ('created_date_ad', 'created_date_bs', 'created_by')


class OrderSummaryDetailSerializer(serializers.ModelSerializer):
    item_category_name = serializers.ReadOnlyField(source='item.item_category.name', allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(
        source='created_by.user_name', allow_null=True
    )

    class Meta:
        model = OrderDetail
        exclude = ['order_main']


class AdvancedDepositPaymentDetailReportSerializer(serializers.ModelSerializer):
    payment_mode_name = serializers.ReadOnlyField(source='payment_mode.name', allow_null=True)

    class Meta:
        model = AdvanceDepositPaymentDetail
        exclude = ['advance_deposit']
        read_only_fields = ['payment_mode_name']


class AdvancedDepositReportSerializer(serializers.ModelSerializer):
    advance_deposit_payment_details = AdvancedDepositPaymentDetailReportSerializer(many=True)

    class Meta:
        model = AdvanceDeposit
        exclude = ['order_main']


class OrderSummaryMainSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_details = OrderSummaryDetailSerializer(many=True)
    advance_deposits = AdvancedDepositReportSerializer(many=True)
    status_display = serializers.ReadOnlyField(source='get_status_display', allow_null=True)
    # customer_order_additional_charges = CustomerOrderAdditionalChargeSerializer(many=True)
    total_advanced_deposit = serializers.SerializerMethodField()

    class Meta:
        model = OrderMain
        fields = "__all__"

    def get_total_advanced_deposit(self, order_main):
        order_main_id = order_main.id
        amount = sum(AdvanceDeposit.objects.filter(order_main=order_main_id).values_list('amount', flat=True))
        return amount


class SaveOrderUpdateTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'customer', 'no_of_attendant', 'status']


class SaveOrderDetailSerializer(serializers.ModelSerializer):
    item_category_name = serializers.ReadOnlyField(source='item.item_category.name', allow_null=True)
    item_name = serializers.ReadOnlyField(source='item.name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(
        source='created_by.user_name', allow_null=True
    )

    class Meta:
        model = OrderDetail
        exclude = ['order_main']
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']


class SaveOrderSerializer(serializers.ModelSerializer):
    customer_first_name = serializers.ReadOnlyField(source='customer.first_name', allow_null=True)
    customer_last_name = serializers.ReadOnlyField(source='customer.last_name', allow_null=True)
    created_by_user_name = serializers.ReadOnlyField(source='created_by.user_name', allow_null=True)
    order_details = SaveOrderDetailSerializer(many=True)

    class Meta:
        model = OrderMain
        fields = "__all__"
        read_only_fields = ['created_date_ad', 'created_date_bs', 'created_by']

    def create(self, validated_data):
        self.create_validate(validated_data)
        date_now = timezone.now()
        order_details = validated_data.pop('order_details')
        if not order_details:
            raise serializers.ValidationError("Please provide at least one order detail")

        validated_data['created_by'] = current_user.get_created_by(self.context)
        order_main = OrderMain.objects.create(**validated_data, created_date_ad=date_now)

        # all the order are stored in OrderDetail
        for detail in order_details:
            OrderDetail.objects.create(**detail, order_main=order_main,
                                       created_by=validated_data['created_by'],
                                       created_date_ad=date_now)

        return order_main

    def update(self, instance, validated_data):
        self.validate_partial_update(instance, validated_data)
        date_now = timezone.now()
        # data that are popped from order_details are saved in order_details/ order to be added are passed
        order_details = validated_data.pop('order_details')

        # update OrderMain Fields
        instance.total_discount = validated_data['total_discount']
        instance.total_tax = validated_data['total_tax']
        instance.total_discountable_amount = validated_data['total_discountable_amount']
        instance.total_taxable_amount = validated_data['total_taxable_amount']
        instance.total_non_taxable_amount = validated_data['total_non_taxable_amount']
        instance.sub_total = validated_data['sub_total']
        instance.grand_total = validated_data['grand_total']



        # all the order are stored in OrderDetail
        for detail in order_details:
            OrderDetail.objects.create(**detail, created_by=current_user.get_created_by(self.context),
                                       order_main=instance, created_date_ad=date_now)
        # call super to now save modified instance along with the validated data
        instance.save()
        return instance

    def create_validate(self, data):
        quantize_places = Decimal(10) ** -2
        # initialize variables to check

        sub_total = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_discountable_amount = Decimal('0.00')
        total_taxable_amount = Decimal('0.00')
        total_nontaxable_amount = Decimal('0.00')
        total_tax = Decimal('0.00')
        grand_total = Decimal('0.00')
        customer_order_details = data['order_details']

        for customer_order in customer_order_details:
            customer_order_detail = {}
            key_values = zip(customer_order.keys(), customer_order.values())
            for key, values in key_values:
                customer_order_detail[key] = values

            # validation for amount values less than or equal to 0 "Zero"
            if customer_order_detail['tax_rate'] < 0 or customer_order_detail['discount_rate'] < 0 or \
                    customer_order_detail['sale_cost'] < 0:
                raise serializers.ValidationError({
                    f'item {customer_order_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                                  ' cannot be less than 0'})

            if customer_order_detail['qty'] <= 0 or customer_order_detail['sale_cost'] <= 0:
                raise serializers.ValidationError({
                    f'item {customer_order_detail["item"].name}': 'values in fields quantity, sale_cost cannot be less than'
                                                                  ' or equals to 0'})
            if customer_order_detail['discount_rate'] > 100:
                raise serializers.ValidationError(
                    {f'item {customer_order_detail["item"].name}': 'Discount rate can not be greater than 100.'})

            # validation for gross_amount
            gross_amount = customer_order_detail['sale_cost'] * customer_order_detail['qty']
            gross_amount = gross_amount.quantize(quantize_places)
            if gross_amount != customer_order_detail['gross_amount']:
                raise serializers.ValidationError(
                    {
                        f'item {customer_order_detail["item"].name}': ' gross_amount calculation not valid : should be {}'.format(
                            gross_amount)})
            sub_total += gross_amount
            # validation for discount amount
            if customer_order_detail['discountable'] is True:
                total_discountable_amount = total_discountable_amount + customer_order_detail['gross_amount']
                discount_rate = (customer_order_detail['discount_amount'] *
                                 Decimal('100')) / (customer_order_detail['sale_cost'] *
                                                    customer_order_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                if discount_rate != customer_order_detail['discount_rate']:
                    raise serializers.ValidationError(
                        {
                            f'item {customer_order_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + customer_order_detail['discount_amount']
            elif customer_order_detail['discountable'] is False and customer_order_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                                       f'discount_amount {customer_order_detail["discount_amount"]} can not be '
                                                       f'given to item with discountable = False'})

            # validation for tax amount
            probable_taxable_amount = gross_amount - customer_order_detail['discount_amount']
            if customer_order_detail['taxable'] is True:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = customer_order_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != customer_order_detail['tax_amount']:
                    raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                                           f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif customer_order_detail['taxable'] is False:
                if customer_order_detail['tax_rate'] != 0 or customer_order_detail['tax_amount'] != 0:
                    raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                                           "taxable = False, tax_rate and tax_amount should be 0"})
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((customer_order_detail['sale_cost'] *
                                           customer_order_detail['qty'] *
                                           customer_order_detail['discount_rate']) / Decimal('100'))) + \
                         ((gross_amount - (customer_order_detail['sale_cost'] *
                                           customer_order_detail['qty'] *
                                           customer_order_detail['discount_rate']) / Decimal('100')) *
                          customer_order_detail['tax_rate'] / Decimal('100'))
            net_amount = net_amount.quantize(quantize_places)
            if net_amount != customer_order_detail['net_amount']:
                raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                                       f'net_amount calculation not valid : should be {net_amount}'})
            grand_total = grand_total + net_amount

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                f'total_discountable_amount calculation {data["total_discountable_amount"]} not valid: should be {total_discountable_amount}'
            )
        # # Adding of additional charge in grand total
        # grand_total = grand_total + add_charge
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                f'grand_total calculation {data["grand_total"]} not valid: should be {grand_total}'
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

        return data

    def validate_partial_update(self, instance, data):
        # raise ValidationError("this is error")
        order_main = instance
        quantize_places = Decimal(10) ** -2
        # initialize variables to check

        sub_total = order_main.sub_total
        total_discount = order_main.total_discount
        total_discountable_amount = order_main.total_discountable_amount
        total_taxable_amount = order_main.total_taxable_amount
        total_nontaxable_amount = order_main.total_non_taxable_amount
        total_tax = order_main.total_tax
        grand_total = order_main.grand_total
        customer_order_details = data['order_details']

        for customer_order in customer_order_details:
            customer_order_detail = {}
            key_values = zip(customer_order.keys(), customer_order.values())
            for key, values in key_values:
                customer_order_detail[key] = values

            # validation for amount values less than or equal to 0 "Zero"
            if customer_order_detail['tax_rate'] < 0 or customer_order_detail['discount_rate'] < 0 or \
                    customer_order_detail['sale_cost'] < 0:
                raise serializers.ValidationError({
                    f'item {customer_order_detail["item"].name}': 'values in fields, tax_rate, discount_rate, sale_cost'
                                                                  ' cannot be less than 0'})

            if customer_order_detail['qty'] <= 0 or customer_order_detail['sale_cost'] <= 0:
                raise serializers.ValidationError({
                    f'item {customer_order_detail["item"].name}': 'values in fields quantity, sale_cost cannot be less than'
                                                                  ' or equals to 0'})
            if customer_order_detail['discount_rate'] > 100:
                raise serializers.ValidationError(
                    {f'item {customer_order_detail["item"].name}': 'Discount rate can not be greater than 100.'})

            # validation for gross_amount
            gross_amount = customer_order_detail['sale_cost'] * customer_order_detail['qty']
            gross_amount = gross_amount.quantize(quantize_places)
            if gross_amount != customer_order_detail['gross_amount']:
                raise serializers.ValidationError(
                    {
                        f'item {customer_order_detail["item"].name}': ' gross_amount calculation not valid : should be {}'.format(
                            gross_amount)})
            sub_total += gross_amount
            # validation for discount amount
            if customer_order_detail['discountable'] is True:
                total_discountable_amount = total_discountable_amount + customer_order_detail['gross_amount']
                discount_rate = (customer_order_detail['discount_amount'] *
                                 Decimal('100')) / (customer_order_detail['sale_cost'] *
                                                    customer_order_detail['qty'])
                discount_rate = discount_rate.quantize(quantize_places)
                if discount_rate != customer_order_detail['discount_rate']:
                    raise serializers.ValidationError(
                        {
                            f'item {customer_order_detail["item"].name}': f'discount_rate calculation not valid : should be {discount_rate}'})
                total_discount = total_discount + customer_order_detail['discount_amount']
            elif customer_order_detail['discountable'] is False and customer_order_detail['discount_amount'] > 0:
                raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                           f'discount_amount {customer_order_detail["discount_amount"]} can not be '
                                           f'given to item with discountable = False'})

            # validation for tax amount
            probable_taxable_amount = gross_amount - customer_order_detail['discount_amount']
            if customer_order_detail['taxable'] is True:
                total_taxable_amount = total_taxable_amount + probable_taxable_amount
                tax_amount = customer_order_detail['tax_rate'] * probable_taxable_amount / Decimal('100')
                tax_amount = tax_amount.quantize(quantize_places)
                if tax_amount != customer_order_detail['tax_amount']:
                    raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                               f'tax_amount calculation not valid : should be {tax_amount}'})
                total_tax = total_tax + tax_amount
            elif customer_order_detail['taxable'] is False:
                if customer_order_detail['tax_rate'] != 0 or customer_order_detail['tax_amount'] != 0:
                    raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                               "taxable = False, tax_rate and tax_amount should be 0"})
                total_nontaxable_amount = total_nontaxable_amount + probable_taxable_amount

            # validation for net_amount
            net_amount = (gross_amount - ((customer_order_detail['sale_cost'] *
                                           customer_order_detail['qty'] *
                                           customer_order_detail['discount_rate']) / Decimal('100'))) + \
                         ((gross_amount - (customer_order_detail['sale_cost'] *
                                           customer_order_detail['qty'] *
                                           customer_order_detail['discount_rate']) / Decimal('100')) *
                          customer_order_detail['tax_rate'] / Decimal('100'))
            net_amount = net_amount.quantize(quantize_places)
            if net_amount != customer_order_detail['net_amount']:
                raise serializers.ValidationError({f'item {customer_order_detail["item"].name}':
                                           f'net_amount calculation not valid : should be {net_amount}'})
            grand_total = grand_total + net_amount

        # validation for total_discountable_amount
        if total_discountable_amount != data['total_discountable_amount']:
            raise serializers.ValidationError(
                f'total_discountable_amount calculation {data["total_discountable_amount"]} not valid: should be {total_discountable_amount}'
            )
        # # Adding of additional charge in grand total
        # grand_total = grand_total + add_charge
        if grand_total != data['grand_total']:
            raise serializers.ValidationError(
                f'grand_total calculation {data["grand_total"]} not valid: should be {grand_total}'
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


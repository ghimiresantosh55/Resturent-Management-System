# Django
from django.db import models
from django.utils import timezone
# User-defined models (import)
from src.core_app.models import NowTimestampAndUserModel, PaymentMode
from src.customer.models import Customer
from src.item.models import Item, ItemCategory
from src.purchase.models import PurchaseDetail
from src.core_app.models import DiscountScheme
from src.customer_order.models import OrderMain, OrderDetail
from src.core_app.models import AdditionalChargeType
from src.rims_setup.models import Table
# import for log
from log_app.models import LogBase
from simple_history import register


class SaleMain(NowTimestampAndUserModel):
    SALE_TYPE = (
        (1, "SALE"),
        (2, "RETURN")
    )

    PAY_TYPE = (
        (1, "CASH"),
        (2, "CREDIT")
    )

    sale_no = models.CharField(max_length=20, unique=True,
                               help_text="Sale no. should be max. of 20 characters")
    table = models.ForeignKey(Table, on_delete=models.PROTECT, null=True, blank=True)
    sale_type = models.PositiveIntegerField(choices=SALE_TYPE, default=1,
                                            help_text="where 1=Sale, 2=Return")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Sub total can have max value upto=9999999999.99 and default=0.0")
    discount_scheme = models.ForeignKey(DiscountScheme, on_delete=models.PROTECT, blank=True, null=True)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                        help_text="Discount rate if applicable, default=0.0 and max_value upto=100.00")
    total_discountable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount can have max value upto=9999999999.99 and default=0.0")
    total_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                               help_text="Total taxable amount can have max value upto=9999999999.99 and default=0.0")
    total_non_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                   help_text="Total nontaxable amount can have max value upto=9999999999.99 and default=0.0")
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                         help_text="Total discount can have max value upto=9999999999.99 and default=0.0")
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Total tax can have max value upto=9999999999.99 and default=0.0")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                      help_text="Grand total can have max value upto=9999999999.99 and default=0.0")
    pay_type = models.PositiveIntegerField(choices=PAY_TYPE, default=1,
                                           help_text="Pay type like 1 = CASH, 2 = CREDIT")
    ref_by = models.CharField(max_length=30, blank=True,
                              help_text="Ref by should be max. of 30 characters")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, help_text="null =True", null=True, blank=True)
    remarks = models.CharField(max_length=100, blank=True,
                               help_text="Remarks should be max. of 100 characters and blank=True")
    ref_sale_main = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    ref_order_main = models.ForeignKey(OrderMain, on_delete=models.CASCADE, blank=True, null=True)
    # ird fields
    synced_with_ird = models.BooleanField(default=False)
    real_time_upload = models.BooleanField(default=False)

    def __str__(self):
        return "id {} : sale {}".format(self.id, self.sale_no)


register(SaleMain, app="log_app", table_name="sale_salemain_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class SaleDetail(NowTimestampAndUserModel):
    sale_main = models.ForeignKey(SaleMain, default=False, related_name="sale_details",
                                  on_delete=models.PROTECT)
    item = models.ForeignKey(Item, default=False, on_delete=models.PROTECT)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                               help_text="cost can have max value upto=9999999999.99 and default=0.0")
    qty = models.DecimalField(max_digits=12, decimal_places=2,
                              help_text="Purchase quantity can have max value upto=9999999999.99 and min_value=0.0")
    taxable = models.BooleanField(default=True, help_text="Check if item is taxable")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                   help_text="Tax rate if item is taxable, max_value=100.00 and default=0.0")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                     help_text="Tax amount can have max value upto=9999999999.99 and default=0.0")
    discountable = models.BooleanField(default=True, help_text="Check if item is discountable")
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                        help_text="Discount rate if item is discountable, max_value=100.00 and default=0.0")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                          help_text="Discount amount can have max value upto=9999999999.99 and default=0.0")
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                       help_text="Gross amount can have max value upto=9999999999.99 and default=0.0")
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                     help_text="Net amount can have max value upto=9999999999.99 and default=0.0")
    ref_purchase_detail = models.ForeignKey(PurchaseDetail, blank=True, null=True,
                                            related_name="purchase_details", on_delete=models.PROTECT)
    ref_sale_detail = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    ref_order_detail = models.ForeignKey(OrderDetail, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return "id {} : sale {}".format(self.id, self.sale_main)


register(SaleDetail, app="log_app", table_name="sale_saledetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class SalePaymentDetail(NowTimestampAndUserModel):
    sale_main = models.ForeignKey(SaleMain, on_delete=models.PROTECT, related_name="payment_details")
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                 help_text="Amount can have max value upto=9999999999.99 and min_value=0.0")
    remarks = models.CharField(max_length=50, blank=True,
                               help_text="Remarks can have max upto 50 characaters and blank=True")

    def __str__(self):
        return "id {} : sale {}".format(self.id, self.sale_main)


register(SalePaymentDetail, app="log_app", table_name="sale_salepaymentdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class SaleAdditionalCharge(NowTimestampAndUserModel):
    charge_type = models.ForeignKey(AdditionalChargeType, on_delete=models.PROTECT)
    sale_main = models.ForeignKey(SaleMain, on_delete=models.PROTECT, related_name="sale_additional_charges")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    remarks = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return "id {} purchase {} charge {}".format(self.id, self.sale_main.order_no, self.charge_type.name)


register(SaleAdditionalCharge, app="log_app", table_name="sale_saleadditionalcharge_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


# model to be synced with IRD

class IRDUploadLog(NowTimestampAndUserModel):
    sale_main = models.ForeignKey(SaleMain, on_delete=models.PROTECT)
    status_code = models.PositiveSmallIntegerField()
    response_message = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_date_ad = timezone.now()
        super().save(*args, **kwargs)


class SalePrintLog(NowTimestampAndUserModel):
    sale_main = models.ForeignKey(SaleMain, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.id}'


register(SalePrintLog, app="log_app", table_name="core_app_saleprintlog_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])

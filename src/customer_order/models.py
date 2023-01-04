# Django
from django.db import models
from src.item.models import Item
from src.core_app.models import NowTimestampAndUserModel, DiscountScheme, PaymentMode
from src.rims_setup.models import Table, Block
from src.customer.models import Customer
from utils.functions.date_converter import ad_to_bs_converter
# imports for log
from log_app.models import LogBase
from simple_history import register


class OrderMain(NowTimestampAndUserModel):
    STATUS_TYPE = (
        (1, "PENDING"),
        (2, "BILLED"),
        (3, "CANCELLED")
    )
    ORDER_TYPE = (
        (1, "ON-TABLE"),
        (2, "TAKE-AWAY"),
        (3, "ONLINE")
    )

    order_no = models.CharField(max_length=20, unique=True, help_text="Order Id should be max. of 10 characters")
    order_type = models.PositiveIntegerField(choices=ORDER_TYPE, default=1, help_text="Where 1 = ON-TABLE, 2=TAKE-AWAY, 3 = ONLINE")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, blank=True, null=True)
    table = models.ForeignKey(Table, on_delete=models.PROTECT, blank=True, null=True)
    status = models.PositiveIntegerField(choices=STATUS_TYPE, default=1, help_text="Where 1 = PENDING,2=BILLED, 3 = CANCELLED")
    discount_scheme = models.ForeignKey(DiscountScheme, on_delete=models.PROTECT, blank=True, null=True)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, help_text="Total discount")
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, help_text="Total tax")
    total_discountable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                    help_text="Total discountable amount")
    total_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                               help_text="Total taxable amount")
    total_non_taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                                   help_text="Total nontaxable amount")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, help_text="Sub total")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, help_text="Grand total")
    delivery_date_ad = models.DateField(max_length=10, help_text="Bill Date AD", blank=True, null=True)
    delivery_date_bs = models.CharField(max_length=10, help_text="Bill Date BS", blank=True)
    delivery_location = models.CharField(max_length=100, blank=True, help_text="Location should be max. of 100 characters")
    remarks = models.CharField(max_length=100, blank=True, help_text="Remarks should be max. of 100 characters")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id}:{self.order_no}"

    def save(self, *args, **kwargs):
        if self.delivery_date_ad is not None:
            self.delivery_date_bs = ad_to_bs_converter(self.delivery_date_ad)
        super().save(*args, **kwargs)


register(OrderMain, app="log_app", table_name="customer_order_ordermain_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class OrderDetail(NowTimestampAndUserModel):
    order_main = models.ForeignKey(OrderMain, on_delete=models.PROTECT, related_name='order_details')
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    qty = models.DecimalField(max_digits=12, decimal_places=2)
    sale_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="sale cost of order default=0.00")
    discountable = models.BooleanField(default=True, help_text="Check if item is discountable default=True")
    taxable = models.BooleanField(default=True, help_text="Check if item is discountable default=True")
    tax_rate = models.DecimalField(max_digits=19, decimal_places=2, default=0.00,
                                   help_text="Tax rate if food is taxable")
    tax_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0.00)
    discount_rate = models.DecimalField(max_digits=19, decimal_places=2, default=0.00,
                                        help_text="Discount rate if food is taxable")
    discount_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0.00)
    gross_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0.00)
    cancelled = models.BooleanField(default=False)
    remarks = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"order id:{self.id} - {self.item.name}"


register(OrderDetail, app="log_app", table_name="customer_order_orderdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


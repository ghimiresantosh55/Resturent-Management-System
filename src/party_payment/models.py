from django.db import models
from src.core_app.models import NowTimestampAndUserModel, PaymentMode
from src.purchase.models import PurchaseMain
# log imprrt
from log_app.models import LogBase
from simple_history import register


class PartyClearance(NowTimestampAndUserModel):
    PAYMENT_TYPE = (
        (1, "PAYMENT"),
        (2, "REFUND"),
    )

    purchase_main = models.ForeignKey(PurchaseMain, on_delete=models.PROTECT)
    payment_type = models.PositiveIntegerField(choices=PAYMENT_TYPE, default=0,
                                               help_text="Where 1 = PAYMENT, 2 = REFUND")
    receipt_no = models.CharField(max_length=20, help_text="Receipt no can have max of 20 characters")

    total_amount = models.DecimalField(max_digits=12, decimal_places=2,
                                       help_text="max_value upto 9999999999.99 and min_vale=0.0")
    remarks = models.CharField(max_length=50, blank=True, help_text="Remarks can be max upto 50 characters, blank=True")
    ref_party_clearance = models.ForeignKey('self', blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return f"id : {self.id}"


register(PartyClearance, app="log_app", table_name="party_payment_partyclearance_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PartyPaymentDetail(NowTimestampAndUserModel):
    party_clearance = models.ForeignKey(PartyClearance, on_delete=models.PROTECT,
                                         related_name="party_payment_details")
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maximum value 9999999999.99, min_value=0.0")
    remarks = models.CharField(max_length=50, blank=True, help_text="Max upto 50 characters, blank=True")

    def __str__(self):
        return f"{self.id}"


register(PartyPaymentDetail, app="log_app", table_name="party_payment_partypaymentdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])

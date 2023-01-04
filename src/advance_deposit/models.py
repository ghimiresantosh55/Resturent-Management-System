from django.db import models
from src.core_app.models import NowTimestampAndUserModel, DiscountScheme
from django.db import models
from src.customer_order.models import OrderMain
from src.sale.models import SaleMain
from src.core_app.models import PaymentMode
import nepali_datetime
# log import
from log_app.models import LogBase
from simple_history import register
# Create your models here.
"""____________________________________________Models for Advance Payment__________________________________________"""


class AdvanceDeposit(NowTimestampAndUserModel):
    DEPOSIT_TYPE = (
        (1, "DEPOSIT"),
        (2, "DEPOSIT-RETURN"),
    )

    order_main = models.ForeignKey(OrderMain, on_delete=models.PROTECT, related_name="advance_deposits")
    advance_deposit_type = models.PositiveIntegerField(choices=DEPOSIT_TYPE,
                                                        help_text="Advance Deposit type like 1= Deposit, 2 = Return")
    # sale_main is updated when order is converted into bill else it remains null/blank
    sale_main = models.ForeignKey(SaleMain, on_delete=models.PROTECT, related_name="sale_main",
                                    blank=True, null=True)
    # DE for deposit, DR for deposit return
    deposit_no = models.CharField(max_length=20, help_text="max deposit_no should not be greater than 13")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maximum value upto 99999999999.99" )
    remarks = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.id}"


register(AdvanceDeposit, app="log_app", table_name="advance_deposit_advancedeposit_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AdvanceDepositPaymentDetail(NowTimestampAndUserModel):
    advance_deposit = models.ForeignKey(AdvanceDeposit, on_delete=models.PROTECT, related_name="advance_deposit_payment_details")
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maximum value upto 99999999999.99")
    remarks = models.CharField(max_length=50, blank=True, help_text="remarks can be upto 50 characters")

    def __str__(self):
        return f"{self.id}"


register(AdvanceDepositPaymentDetail, app="log_app", table_name="advance_deposit_advancedepositpaymentdetail_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


'''For saving Advance deposit from Customer Order'''
'''
 "advance_deposit":{
  "amount": 0,
  "advance_deposit_type": 1,
  "remarks":"remarks for advanced deposit",
    "advance_deposit_payment_details":[{
       "payment_mode":1,
       "amount": 500,
         "remarks": "remarks for mode"
         },
         {
        "payment_mode":2,
        "amount": 300,
        "remarks": "remarks for mode"
        }]
 }
'''
from django.db import models
from src.core_app.models import NowTimestampAndUserModel
from src.customer.models import Customer

# import for log
from log_app.models import LogBase
from simple_history import register


class Block(NowTimestampAndUserModel):
    name = models.CharField(max_length=20, unique=True)
    active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name}"


register(Block, app="log_app", table_name="rims_setup_block_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Table(NowTimestampAndUserModel):
    STATUS_TYPE = (
        (1, "OCCUPIED"),
        (2, "VACANT"),
        (3, "RESERVED")
    )
    name = models.CharField(max_length=20)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, blank=True, null=True)
    capacity = models.IntegerField()
    no_of_attendant = models.IntegerField(blank=True, default=0)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, help_text="ForeignKey")
    status = models.PositiveIntegerField(choices=STATUS_TYPE, default=2, help_text="Where 1= OCCUPIED, "
                                                                                   "2 = VACANT, 3 = RESERVED")
    display_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


register(Table, app="log_app", table_name="rims_setup_table_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])



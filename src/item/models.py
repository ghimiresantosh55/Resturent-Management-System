from django.db import models
from src.core_app.models import NowTimestampAndUserModel
from django.core.exceptions import ValidationError
from django.conf import settings
# imports for log
from simple_history import register
from log_app.models import LogBase


def validate_image(image):
    file_size = image.size
    limit_byte_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size/1024
        # converting into MB
        f = f/1024
        raise ValidationError("Max size of file is %s MB" % f)


class ItemCategory(NowTimestampAndUserModel):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True,
                            help_text="Item code can be max. of 10 characters")
    display_order = models.IntegerField(default=0, help_text="Display order for ordering, default=0")
    active = models.BooleanField(default=True, )

    def __str__(self):
        return f"id:{self.id}-{self.name}"


register(ItemCategory, app="log_app", table_name="item_itemcategory_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class ItemSubCategory(NowTimestampAndUserModel):
    item_category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT, null=True, blank=True)
    code = models.CharField(max_length=10, unique=True, blank=True,
                            help_text="Item code can be max. of 10 characters")
    display_order = models.IntegerField(default=0, help_text="Display order for ordering, default=0")
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"id:{self.id}-{self.name}"


register(ItemSubCategory, app="log_app", table_name="item_itemsubcategory_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Item(NowTimestampAndUserModel):
    ITEM_TYPE = (
        (1, "INVENTORY"),
        (2, "SALE"),
        (3, "BOTH")
    )

    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True,
                            help_text="Item code should be max. of 10 characters")
    item_type = models.PositiveIntegerField(choices=ITEM_TYPE,
                                            help_text="Item type like 1=INVENTORY, 2=SALE, 3=BOTH")
    stock_alert_qty = models.IntegerField(default=1, help_text="Quantity for alert/warning")
    item_category = models.ForeignKey(ItemCategory, on_delete=models.PROTECT)
    item_sub_category = models.ForeignKey(ItemSubCategory, on_delete=models.PROTECT, blank=True, null=True)
    location = models.CharField(max_length=10, help_text="Physical location of item, max length can be of 10 characters")

    description = models.CharField(max_length=50, blank=True)
    taxable = models.BooleanField(default=True, help_text="Check if item is taxable, default=True")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                                   help_text="Tax rate if item is taxable, default=0.0 and can be upto 100.00")
    discountable = models.BooleanField(default=True,
                                       help_text="Check if item is discountable, default=True")
    expirable = models.BooleanField(default=True,
                                    help_text="Check if item is expirable, default=True")
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                        help_text="Max value purchase_cost can be upto 9999999999.99")
    sale_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0,
                                    help_text="Max value sale_cost can be upto 9999999999.99")
    recipe = models.CharField(max_length=250, blank=True)
    image = models.ImageField(upload_to='item/', validators=[validate_image], blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"id:{self.id}-{self.name}"


register(Item, app="log_app", table_name="item_item_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])

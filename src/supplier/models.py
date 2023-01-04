# Django
from django.db import models

# User-defined models (import)
from src.core_app.models import NowTimestampAndUserModel, Country
from django.conf import settings
from django.core.exceptions import ValidationError

# import for log
from log_app.models import LogBase
from simple_history import register


def validate_image(image):
    file_size = image.size
    limit_byte_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size / 1024
        # converting into MB
        f = f / 1024
        raise ValidationError("Max size of file is %s MB" % f)


class Supplier(NowTimestampAndUserModel):
    TAX_REG_SYSTEM_TYPES = (
        (1, "VAT"),
        (2, "PAN"),
        (3, "N/A")
    )
    first_name = models.CharField(max_length=40, help_text="First name can be max. of 40 characters")
    middle_name = models.CharField(max_length=40, blank=True,
                                   help_text="Middle can can be max. of 40 characters, blank=True")
    last_name = models.CharField(max_length=40, help_text="Last name can be max. of 40 characters")
    address = models.CharField(max_length=50, help_text="Address can be max. of 50 characters")
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    phone_no = models.CharField(max_length=15, blank=True, help_text="Phone no. can be max. of 15 characters, blank=True")
    mobile_no = models.CharField(max_length=15, blank=True, help_text="Mobile no. can be max. of 15 characters, blank=True")
    email_id = models.CharField(max_length=50, blank=True, help_text="Email Id can be max. of 50 characters, blank=True")
    tax_reg_system = models.PositiveIntegerField(choices=TAX_REG_SYSTEM_TYPES, default=3, help_text="by default=1")
    pan_vat_no = models.CharField(max_length=9, blank=True, help_text="PAN can be max. of 15 characters, blank=True")
    image = models.ImageField(upload_to='supplier/', validators=[validate_image], null=True,
                              blank=True, help_text="max image size can be 2 MB")
    active = models.BooleanField(default=True, help_text="by default active=True")

    def __str__(self):
        return "id {}: {} {} {}".format(self.id, self.first_name, self.middle_name, self.last_name)


register(Supplier, app="log_app", table_name="supplier_supplier_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])

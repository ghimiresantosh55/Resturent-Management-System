# Django
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
# custom functions import
from utils.functions.date_converter import ad_to_bs_converter
# log import
from log_app.models import LogBase
from simple_history import register
User = get_user_model()


def validate_image(image):
    file_size = image.size
    limit_byte_size = settings.MAX_UPLOAD_SIZE
    if file_size > limit_byte_size:
        # converting into kb
        f = limit_byte_size / 1024
        # converting into MB
        f = f / 1024
        raise ValidationError("Max size of file is %s MB" % f)


class NowTimestampAndUserModel(models.Model):
    created_date_ad = models.DateTimeField()
    created_date_bs = models.CharField(max_length=10)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        date_bs = ad_to_bs_converter(self.created_date_ad)
        self.created_date_bs = date_bs

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Country(NowTimestampAndUserModel):
    name = models.CharField(max_length=50, unique=True,
                            help_text="Name of the country can have max upto 50 characters, unique=True")
    country_code = models.CharField(max_length=5, blank=True, null=True, help_text="country code max length 5")
    phone_code = models.CharField(max_length=5, blank=True, null=True, help_text="country code max length 5")
    currency_name = models.CharField(max_length=50, blank=True, null=True, help_text="country code max length 50")
    currency_symbol = models.CharField(max_length=3, blank=True, null=True, help_text="country code max length 3")
    currency_code = models.CharField(max_length=3, blank=True, null=True, help_text="country code max length 3")
    flag_image = models.ImageField(upload_to='country_flag/', validators=[validate_image],
                                   blank=True, help_text="Image can be max of 2 MB size, blank=True")
    active = models.BooleanField(default=True, help_text="By default= true")

    def __str__(self):
        return f"{self.name}"


register(Country, app="log_app", table_name="core_app_country_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Province(NowTimestampAndUserModel):
    name = models.CharField(max_length=50, unique=True,
                            help_text="Province name can be max. of 50 characters and unique=True")
    active = models.BooleanField(default=True, help_text="by default=True")

    def __str__(self):
        return f"{self.name}"


register(Province, app="log_app", table_name="core_app_province_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class District(NowTimestampAndUserModel):
    name = models.CharField(max_length=50, unique=True,
                            help_text="District name can be max. of 50 characters and unique=True")
    province = models.ForeignKey(Province, on_delete=models.PROTECT)
    active = models.BooleanField(default=True, help_text="by default=True")

    def __str__(self):
        return f"{self.name}"


register(District, app="log_app", table_name="core_app_district_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class OrganizationSetup(NowTimestampAndUserModel):
    name = models.CharField(max_length=100, unique=True,
                            help_text="Organization name should be maximum of 100 characters")
    address = models.CharField(max_length=100, unique=True, blank=True,
                               help_text="Organization name should be maximum of 100 characters")
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    phone_no_1 = models.CharField(max_length=15, unique=True, blank=True,
                                  help_text="Phone no should be maximum of 15 characters")
    phone_no_2 = models.CharField(max_length=15, blank=True, help_text="Phone no should be maximum of 15 characters")
    mobile_no = models.CharField(max_length=15, unique=True, blank=True,
                                 help_text="Mobile no should be maximum of 15 characters")
    pan_no = models.CharField(max_length=15, unique=True, blank=True,
                              help_text="PAN no. should be maximum of 15 characters")
    owner_name = models.CharField(max_length=50, unique=True, blank=True,
                                  help_text="Owner name should be maximum of 50 characters")
    email = models.CharField(max_length=70, unique=True, blank=True,
                             help_text="Email Id. should be maximum of 70 characters")
    website_url = models.CharField(max_length=50, unique=True, blank=True,
                                   help_text="Website address should be maximum of 50 characters")
    logo = models.ImageField(upload_to='organization/', validators=[validate_image], blank=True, help_text="")
    favicon = models.ImageField(upload_to='organization/', validators=[validate_image], blank=True,
                                help_text="")

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)


register(OrganizationSetup, app="log_app", table_name="core_app_organizationsetup_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class OrganizationRule(NowTimestampAndUserModel):
    CUSTOMER_SEQUENCE_TYPE = [
        (1, "AD"),
        (2, "BS"),
        (3, "SEQUENTIAL")
    ]

    CALENDAR_SYSTEM = [
        (1, "AD"),
        (2, "BS")
    ]

    DAYS_OF_WEEK = [
        (1, "SUNDAY"),
        (2, "MONDAY"),
        (3, "TUESDAY"),
        (4, "WEDNESDAY"),
        (5, "THURSDAY"),
        (6, "FRIDAY"),
        (7, "SATURDAY"),
    ]

    TAX_SYSTEM = [
        (1, "VAT"),
        (2, "PAN")
    ]
    customer_seq_type = models.PositiveIntegerField(choices=CUSTOMER_SEQUENCE_TYPE, default=2, \
                                                    help_text="where 1=AD,2=BS,3=SEQUENTIAL  and default=2")
    fiscal_session_type = models.PositiveIntegerField(choices=CALENDAR_SYSTEM, default=2, \
                                                      help_text="Where 1 = AD , 2 = BS and default=2")
    calendar_system = models.PositiveIntegerField(choices=CALENDAR_SYSTEM, default=2, \
                                                  help_text="Where 1 = AD , 2 = BS and default=2")
    enable_print = models.BooleanField(default=True)
    print_preview = models.BooleanField(default=True)
    billing_time_restriction = models.BooleanField(default=False)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    first_day_of_week = models.PositiveIntegerField(choices=DAYS_OF_WEEK, default=1,
                                                    help_text="where 1 = Sunday ---- 7 =Saturday")
    tax_system = models.PositiveIntegerField(choices=TAX_SYSTEM, default=1, help_text="where 1=VAT, 2=PAN")
    round_off_limit = models.PositiveIntegerField(default=2)
    item_expiry_date_sale_threshold = models.PositiveIntegerField(default=30)
    tax_applicable = models.BooleanField(default=True)
    tax_rate = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)],
                                 help_text="Tax rate")

    def __str__(self):
        return "id {} : {}".format(self.id, self.get_calendar_system_display())


register(OrganizationRule, app="log_app", table_name="core_app_organizationrule_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class Bank(NowTimestampAndUserModel):
    name = models.CharField(max_length=50, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)


register(Bank, app="log_app", table_name="core_app_bank_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class BankDeposit(NowTimestampAndUserModel):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    deposit_date_ad = models.DateTimeField()
    deposit_date_bs = models.CharField(max_length=10, blank=True)
    deposit_by = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="User can input value upto 99999999.99")
    remarks = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        date_bs = ad_to_bs_converter(self.deposit_date_ad)
        self.deposit_date_bs = date_bs

        super().save(*args, **kwargs)

    def __str__(self):
        return "id {} : deposited by {} to {} bank".format(self.id, self.deposit_by, self.bank.name)


register(BankDeposit, app="log_app", table_name="core_app_bankdeposit_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class PaymentMode(NowTimestampAndUserModel):
    name = models.CharField(max_length=15, unique=True)
    active = models.BooleanField(default=0)
    remarks = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name}"


register(PaymentMode, app="log_app", table_name="core_app_paymentmode_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class DiscountScheme(NowTimestampAndUserModel):
    name = models.CharField(max_length=50, unique=True, help_text="Discount scheme name must be max 50 characters")
    editable = models.BooleanField(default=False)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                               help_text="Discount Rate default=0.00 max upto 100.00")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


register(DiscountScheme, app="log_app", table_name="core_app_discountscheme_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AdditionalChargeType(NowTimestampAndUserModel):
    name = models.CharField(max_length=50, unique=True,
                            help_text="Additional Charge type name must be max 50 characters")
    active = models.BooleanField(default=True)

    def __str__(self):
        return "id {} : {}".format(self.id, self.name)


register(AdditionalChargeType, app="log_app", table_name="core_app_additionalchargetype_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class TaxGroup(NowTimestampAndUserModel):
    name = models.CharField(max_length=20, unique=True,
                            help_text="Name can have max of 20 characaters and must be unique")
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0,
                               help_text="Default=0.0")
    display_order = models.IntegerField(default=0, help_text="Display order for ordering, default=0")
    active = models.BooleanField(default=True, help_text="By default active=True")


register(TaxGroup, app="log_app", table_name="core_app_taxgroup_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class AppAccessLog(NowTimestampAndUserModel):
    DEVICE_TYPE = [
        (1, "Mobile"),
        (2, "PC"),
        (3, "Tablet"),
        (4, "Other")
    ]
    APP_TYPE = [
        (1, 'Web-App'),
        (2, 'IOS-App'),
        (3, 'Android-App')
    ]
    device_type = models.PositiveBigIntegerField(choices=DEVICE_TYPE, default="NA",
                                                 help_text="where 1=Mobile, 2=PC, 3=Tablet and 4=Other")
    app_type = models.PositiveBigIntegerField(choices=APP_TYPE, default="NA",
                                              help_text="where 1=Web-App, 2=IOS-APP, 3=Android-APP")

    def __str__(self):
        return f'{self.id}'


register(AppAccessLog, app="log_app", table_name="core_app_appaccesslog_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])

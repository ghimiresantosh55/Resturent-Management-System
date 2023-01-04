from django.db import models
from django.conf import settings
from django.utils import timezone
from utils.functions.date_converter import ad_to_bs_converter
import re
from django.core.exceptions import ValidationError
# imports for log
from simple_history import register
from log_app.models import LogBase


class UserGroup(models.Model):
    name = models.CharField(max_length=50, help_text="Name can have max of 50 characters")
    is_active = models.BooleanField(default=True, help_text="default value is True")
    permissions = models.ManyToManyField('UserPermission', blank=True, help_text="Many to many connection with Permissions")
    created_date_ad = models.DateTimeField()
    created_date_bs = models.CharField(max_length=10)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.pk} : {self.name}"

    def save(self, *args, **kwargs):
        # saving created_date_ad and bs, when it is a create operation
        if not self.id and not self.created_date_ad:
            self.created_date_ad = timezone.now()
            date_bs = ad_to_bs_converter(self.created_date_ad)
            self.created_date_bs = date_bs

        super().save(*args, **kwargs)


register(UserGroup, app="log_app", table_name="user_group_customgroup_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


class UserPermissionCategory(models.Model):
    name = models.CharField(max_length=50, help_text="Name can have max of 50 characters")
    created_date_ad = models.DateTimeField(default=timezone.now)
    created_date_bs = models.CharField(max_length=10)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"ID-{self.id} : {self.name}"

    def save(self, *args, **kwargs):
        # saving created_date_ad and bs, when it is a create operation
        if not self.id and not self.created_date_ad:
            self.created_date_ad = timezone.now()
            date_bs = ad_to_bs_converter(self.created_date_ad)
            self.created_date_bs = date_bs

        super().save(*args, **kwargs)


register(UserPermissionCategory, app="log_app", table_name="user_group_permissioncategory_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])


def validate_code_name(self, code_name):
    if not (bool(re.match("^[a-z0-9_]*$", str(code_name)))):
        raise ValidationError("code_name should only contain small letter, numbers and underscores")


class UserPermission(models.Model):
    name = models.CharField(max_length=50, help_text="Name can have max of 50 characters")
    code_name = models.CharField(max_length=50, validators=[validate_code_name], help_text="Code Name can have max of 50 characters")
    category = models.ForeignKey('UserPermissionCategory', on_delete=models.PROTECT, null=True, blank=True,
                                 help_text="foreign key to UserPermissionCategory")
    created_date_ad = models.DateTimeField(default=timezone.now)
    created_date_bs = models.CharField(max_length=10)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return f"{self.category} : {self.code_name} "

    def save(self, *args, **kwargs):
        
        # saving created_date_ad and bs, when it is a create operation
        if not self.id and not self.created_date_ad:
            self.created_date_ad = timezone.now()
            date_bs = ad_to_bs_converter(self.created_date_ad)
            self.created_date_bs = date_bs
        super().save(*args, **kwargs)


register(UserPermission, app="log_app", table_name="user_group_custompermission_log",
         custom_model_name=lambda x: f'Log{x}',
         use_base_model_db=False, history_user_id_field=models.IntegerField(null=True),
         excluded_fields=['created_date_ad', 'created_date_bs', 'created_by'], bases=[LogBase])




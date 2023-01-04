from django.db import models
import re
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

def validate_schema_name(schema_name):
    if not (bool(re.match("^[a-z0-9_]*$", str(schema_name)))):
        raise ValidationError("schema_name should only contain small letter, numbers and underscores")


class Tenant(models.Model):
    name = models.CharField(max_length=100, unique=True)
    schema_name = models.CharField(max_length=100, validators=[validate_schema_name], unique=True)
    sub_domain = models.CharField(max_length=300, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} : {self.sub_domain}"

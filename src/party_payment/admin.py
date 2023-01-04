from django.contrib import admin
from .models import PartyClearance, PartyPaymentDetail


# Register your models here.

class PartyPaymentDetailAdmin(admin.ModelAdmin):
    list_display = ['id']


admin.site.register(PartyPaymentDetail, PartyPaymentDetailAdmin)
admin.site.register(PartyClearance)

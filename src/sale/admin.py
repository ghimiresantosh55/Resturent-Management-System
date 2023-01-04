from django.contrib import admin
from .models import SaleMain, SaleDetail, SalePaymentDetail, SaleAdditionalCharge, SalePrintLog


class SaleMainAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale_no', 'sale_type', 'grand_total', 'pay_type', 'created_date_ad')


class SaleDetailAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'sale_main', 'item', 'net_amount', 'ref_purchase_detail', 'ref_sale_detail', 'ref_order_detail',
        'created_date_ad')


class SalePaymentDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale_main', 'payment_mode', 'amount', 'created_date_ad')


admin.site.register(SaleMain, SaleMainAdmin)
admin.site.register(SaleDetail, SaleDetailAdmin)
admin.site.register(SalePaymentDetail, SalePaymentDetailAdmin)
admin.site.register(SaleAdditionalCharge)
admin.site.register(SalePrintLog)

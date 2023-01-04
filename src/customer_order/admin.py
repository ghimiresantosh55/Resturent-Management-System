from django.contrib import admin
from .models import OrderMain, OrderDetail


class OrderDetailAdmin(admin.ModelAdmin):
    model = OrderDetail
    search_fields = ['id']
    ordering = ['id', 'order_main']
    list_display = ['id', 'order_main']


admin.site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(OrderMain)


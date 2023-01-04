from django.contrib import admin
from .models import Item, ItemCategory, ItemSubCategory

admin.site.register(Item)
admin.site.register(ItemCategory)
admin.site.register(ItemSubCategory)

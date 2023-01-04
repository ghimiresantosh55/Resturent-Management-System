from django.contrib import admin
from .models import UserGroup, UserPermission, UserPermissionCategory
from django.contrib.auth.models import Group


class CustomPermissionAdmin(admin.ModelAdmin):
    model = UserPermission
    search_fields = ('code_name',)
    list_filter = ('category',)


admin.site.unregister(Group)
admin.site.register(UserGroup)
admin.site.register(UserPermission, CustomPermissionAdmin)
admin.site.register(UserPermissionCategory)
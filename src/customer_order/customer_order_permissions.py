from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class CustomerOrderViewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if request.method in SAFE_METHODS and 'view_customer_order' in user_permissions:
            return True
        return False


class CustomerOrderSavePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_customer_order' in user_permissions:
            return True
        return False


class CustomerOrderUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_customer_order' in user_permissions:
            return True
        return False


class CustomerOrderCancelPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'cancel_customer_order' in user_permissions:
            return True
        return False

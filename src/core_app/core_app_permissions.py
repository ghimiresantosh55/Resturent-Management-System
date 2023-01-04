from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class CountryPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_country' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_country' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_country' in user_permissions:
            return True
        return False


class ProvincePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_province' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_province' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_province' in user_permissions:
            return True
        return False


class DistrictPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_district' in user_permissions:
            return True
        if (request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_district' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_district' in user_permissions:
            return True
        return False



class OrganizationRulePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False

        if (request.method in SAFE_METHODS or request.method == 'POST') and 'add_organization_rule' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_organization_rule' in user_permissions:
            return True
        if (request.method in SAFE_METHODS or request.method == 'PATCH') and 'update_organization_rule' in user_permissions:
            return True
        return False


class OrganizationSetupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_organization_setup' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_organization_setup' in user_permissions or
                                               'add_organization_setup' in user_permissions or
                                               'update_organization_setup' in user_permissions):
            return True
        if request.method == 'PATCH' and 'update_organization_setup' in user_permissions:
            return True
        return False


class BankPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_bank' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_bank' in user_permissions or
                                               'update_bank' in user_permissions or
                                               'add_bank' in user_permissions):
            return True
        if request.method == 'PATCH' and 'update_bank' in user_permissions:
            return True
        return False


class BankDepositPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_bank_deposit' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_bank_deposit' in user_permissions or
                                               'add_bank_deposit' in user_permissions or
                                               'update_bank_deposit' in user_permissions):
            return True
        if request.method == 'PATCH' and 'update_bank_deposit' in user_permissions:
            return True
        return False


class PaymentModePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_payment_mode' in user_permissions:
            return True
        elif request.method in SAFE_METHODS and ('view_payment_mode' in user_permissions or
                                                 'add_payment_mode' in user_permissions or
                                                 'update_payment_mode' in user_permissions):
            return True
        elif request.method in SAFE_METHODS and 'approve_purchase_order' in user_permissions:
            return True
        elif request.method in SAFE_METHODS and 'add_purchase' in user_permissions:
            return True
        elif request.method in SAFE_METHODS and 'add_sale' in user_permissions:
            return True
        elif request.method in SAFE_METHODS and 'add_sale_return' in user_permissions:
            return True
        elif request.method == 'PATCH' and 'update_payment_mode' in user_permissions:
            return True
        return False


class DiscountSchemePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if request.method == 'POST' and 'add_discount_scheme' in user_permissions:
            return True
        if request.method in SAFE_METHODS and ('view_discount_scheme' in user_permissions or
                                               'add_discount_scheme' in user_permissions or
                                               'update_discount_scheme' in user_permissions ):
            return True
        if request.method == 'PATCH' and 'update_discount_scheme' in user_permissions:
            return True
        return False


class AdditionalChargeTypePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_additional_charge' in user_permissions:
            return True

        if request.method in SAFE_METHODS and ('view_additional_charge' in user_permissions or
                                               'approve_purchase_order' in user_permissions or
                                               'add_purchase' in user_permissions):
            return True
        if(request.method == 'PATCH' or request.method in SAFE_METHODS) and 'update_additional_charge' in user_permissions:
            return True
        return False


class AppAccessLogPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.is_superuser is True:
            return True
        try:
            user_permissions = request.user.group.permissions.values_list('code_name', flat=True)
        except:
            return False
        if (request.method == 'POST' or request.method in SAFE_METHODS) and 'add_app_access_log' in user_permissions:
            return True
        if request.method in SAFE_METHODS and 'view_app_access_log' in user_permissions:
            return True
        return False
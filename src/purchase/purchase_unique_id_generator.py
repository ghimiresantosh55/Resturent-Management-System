from .models import PurchaseMain, PurchaseOrderMain
from utils.functions.fiscal_year import get_fiscal_year_code_bs
# format order_no according to given digits
PURCHASE_ORDER_LENGTH = 10

fiscal_year_code = get_fiscal_year_code_bs()
# generate unique order_no for purchase_order_main
def generate_order_no(order_type):
    if order_type == 1:
        cancel_count = PurchaseOrderMain.objects.filter(order_type=order_type).count()
        max_id = str(cancel_count + 1)
        unique_id = "PO-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id
    elif order_type == 2:
        cancel_count = PurchaseOrderMain.objects.filter(order_type=order_type).count()
        max_id = str(cancel_count + 1)
        unique_id = "PC-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id
    elif order_type == 3:
        cancel_count = PurchaseOrderMain.objects.filter(order_type=order_type).count()
        max_id = str(cancel_count + 1)
        unique_id = "PA-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
        return unique_id
    else:
        return ValueError


# generate unique order_no for purchase_master
def generate_purchase_no(purchase_type):

    if purchase_type == 1:
        cancel_count = PurchaseMain.objects.filter(purchase_type=purchase_type).count()
        max_id = str(cancel_count + 1)
        unique_id = "PU-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)

        return unique_id
    elif purchase_type == 2:
        cancel_count = PurchaseMain.objects.filter(purchase_type=purchase_type).count()
        max_id = str(cancel_count + 1)
        unique_id = "PR-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)

        return unique_id

    elif purchase_type == 3:
        cancel_count = PurchaseMain.objects.filter(purchase_type=purchase_type).count()
        max_id = str(cancel_count + 1)
        unique_id = "OS-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)

        return unique_id

    elif purchase_type == 4:
        cancel_count = PurchaseMain.objects.filter(purchase_type=purchase_type).count()
        max_id = str(cancel_count + 1)
        unique_id = "AD-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)

        return unique_id

    elif purchase_type == 5:
        cancel_count = PurchaseMain.objects.filter(purchase_type=purchase_type).count()
        max_id = str(cancel_count + 1)
        unique_id = "SU-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)

        return unique_id

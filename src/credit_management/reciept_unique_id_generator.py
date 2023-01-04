from src.credit_management.models import CreditClearance
from utils.functions.fiscal_year import get_fiscal_year_code_bs
from django.utils import timezone
# format order_no according to given digits
PURCHASE_ORDER_LENGTH = 10


# generate unique order_no for purchase_order_main
def get_receipt_no():
    count = CreditClearance.objects.count()
    max_id = str(count + 1)
    fiscal_year_code = get_fiscal_year_code_bs()
    unique_id = "RE-" + fiscal_year_code + "-" + max_id.zfill(PURCHASE_ORDER_LENGTH)
    return unique_id

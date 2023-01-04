from .models import OrderMain
from src.advance_deposit.models import AdvanceDeposit

# format order_no according to given digits
from utils.functions.fiscal_year import get_fiscal_year_code_bs


ORDER_NO_LENGTH = 10


# generate unique order_no for order_main
def generate_customer_order_no():
    cancel_count = OrderMain.objects.count()
    max_id = str(cancel_count + 1)
    fiscal_year_code = get_fiscal_year_code_bs()
    unique_id = "CO-" + fiscal_year_code + "-" + max_id.zfill(ORDER_NO_LENGTH)
    return unique_id


def generate_advanced_deposit_no():
    deposit_count = AdvanceDeposit.objects.count()
    max_id = str(deposit_count + 1)
    fiscal_year_code = get_fiscal_year_code_bs()
    unique_id = "AD-" + fiscal_year_code + "-" + max_id.zfill(ORDER_NO_LENGTH)
    return unique_id

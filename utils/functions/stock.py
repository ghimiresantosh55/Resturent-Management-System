from src.purchase.models import PurchaseDetail
from src.sale.models import SaleDetail
from django.db.models import F
from django.db.models import Case, Value, When
from django.db import models
from django.http import JsonResponse

"""____________________________stock analysis of purchase _______________________________________________________________"""


def get_remaining_qty_of_purchase(ref_id):
    stock = get_purchase_qty(ref_id) - get_purchase_return_qty(ref_id) - \
            get_purchase_sale_qty(ref_id) + get_purchase_sale_return_qty(ref_id)
    return stock


# call value id of PurchaseDetail
def get_purchase_qty(ref_id):
    total_purchase_qty = sum(PurchaseDetail.objects.filter(pk=ref_id)
                             .values_list('qty', flat=True))
    return total_purchase_qty


# call value ref_purchase_detail
def get_purchase_return_qty(ref_id):
    total_purchase_return_qty = sum(
        PurchaseDetail.objects.filter(ref_purchase_detail=ref_id).values_list('qty', flat=True))
    return total_purchase_return_qty


# call value ref_purchase_detail
def get_purchase_sale_qty(ref_id):
    total_sale_qty = sum(
        SaleDetail.objects.filter(ref_purchase_detail=ref_id, sale_main__sale_type=1).values_list('qty', flat=True))
    return total_sale_qty


# call value ref_purchase_detail
def get_purchase_sale_return_qty(ref_id):
    total_sale_return_qty = sum(
        SaleDetail.objects.filter(ref_purchase_detail=ref_id, sale_main__sale_type=2).values_list('qty', flat=True))
    return total_sale_return_qty


"""____________________________stock analysis of items _______________________________________________________________"""


def get_remaining_qty_of_item(item_id):
    stock = get_purchase_qty_of_item(item_id) - \
            get_purchase_return_qty_of_item(item_id) - \
            get_sale_qty_of_item(item_id) + get_sale_return_qty_of_item(item_id)
    return stock


def get_purchase_qty_of_item(item_id):
    total_quantity = sum(
        PurchaseDetail.objects.filter(item=item_id, purchase__purchase_type=1).values_list('qty', flat=True))
    return total_quantity


def get_purchase_return_qty_of_item(item_id):
    total_purchase_return_qty = sum(
        PurchaseDetail.objects.filter(item=item_id, purchase__purchase_type=2).values_list('qty', flat=True))
    return total_purchase_return_qty


def get_sale_qty_of_item(item_id):
    total_sale_qty = sum(
        SaleDetail.objects.filter(item=item_id, sale_main__sale_type=1).values_list('qty', flat=True))
    return total_sale_qty


def get_sale_return_qty_of_item(item_id):
    total_sale_return_qty = sum(
        SaleDetail.objects.filter(item=item_id, sale_main__sale_type=2).values_list('qty', flat=True))
    return total_sale_return_qty


"""_________________________________________ sale stock analysis ___________________________________________"""


def get_sale_return_qty(sale_detail_id):
    stock = sum(SaleDetail.objects.filter(ref_sale_detail=sale_detail_id).values_list('qty', flat=True))
    return stock


def get_sale_remaining_qty(sale_detail_id):
    total_qty = SaleDetail.objects.values_list('qty', flat=True).get(id=sale_detail_id)
    stock = total_qty - get_sale_return_qty(sale_detail_id)
    return stock


"""_______________________________________ Supplier stock analysis ________________________________________"""


# def get_purchase_item_qty_of_supplier(supplier_id):
#     qty = PurchaseDetail.objects.filter(purchase__supplier=supplier_id).


def get_item_ledger(filterset):
    query = PurchaseDetail.objects.all().values('created_date_ad', 'created_date_bs', 'qty') \
        .annotate(item_name=F('item__name'),
                  item=F('item'),
                  supplier_customer_name=F('purchase__supplier__first_name'),
                  supplier_customer=F('purchase__supplier'),
                  batch_no=F('batch_no'),
                  cost=F('purchase_cost'),
                  op_type=Case(
                      When(purchase__purchase_type=1, then=Value('PURCHASE')),
                      When(purchase__purchase_type=2, then=Value('PURCHASE-RETURN')),
                      When(purchase__purchase_type=2, then=Value('OPENING-STOCK')),
                      When(purchase__purchase_type=2, then=Value('STOCK-ADDITION')),
                      When(purchase__purchase_type=2, then=Value('STOCK-SUBTRACTION')),
                      default=Value('N/A'),
                      output_field=models.CharField()))\
        .filter(**filterset) \
        .union(SaleDetail.objects.all().values('created_date_ad', 'created_date_bs', 'qty') \
               .annotate(item_name=F('item__name'),
                         item=F('item'),
                         supplier_customer_name=F('sale_main__customer__first_name'),
                         supplier_customer=F('sale_main__customer'),
                         batch_no=F('ref_purchase_detail__batch_no'),
                         cost=F('cost'),
                         op_type=Case(
                             When(sale_main__sale_type=1, then=Value('SALE')),
                             When(sale_main__sale_type=2, then=Value('SALE-RETURN')),
                             default=Value('N/A'),
                             output_field=models.CharField(),
                             ),

                         ).filter(**filterset), all=True)

    return query

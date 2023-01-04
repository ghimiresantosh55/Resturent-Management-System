# Django-rest-framework
from rest_framework import serializers, viewsets, status
from rest_framework.response import Response
from django.db import transaction
from decimal import Decimal
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from utils.functions.fiscal_year import get_fiscal_year_code_bs
# from requests library
import requests
from django.utils import timezone
import threading
from django.db import connection
from tenant.utils import tenant_schema_from_request

from src.sale.models import SaleDetail, SaleMain, SalePaymentDetail, IRDUploadLog, SaleAdditionalCharge, SalePrintLog
from .sale_unique_id_generator import generate_sale_no
from src.item.models import Item
# import core files
from utils.functions import stock

# filter
from django_filters import DateFromToRangeFilter, FilterSet

# import serializer
from src.sale.serializers import SaleMainSerializer, SaleDetailSerializer, SaveSaleMainSerializer, \
    SaleDetailForSaleReturnSerializer, SalePaymentDetailSerializer
from src.customer.serializers import CustomerSerializer
from src.core_app.models import DiscountScheme, AdditionalChargeType, PaymentMode, OrganizationSetup
from src.core_app.serializers import DiscountSchemeSerializer, AdditionalChargeTypeSerializer, PaymentModeSerializer
from src.customer.models import Customer
from src.customer.serializers import CustomerSerializer
from .sale_permissions import SaleSavePermission, SaleViewPermission, SaleReturnViewPermission, SaleReturnPermission, \
    SaleDetailViewPermission, SalePrintLogPermission
from .serializers import SalePrintLogSerializer, UpdateCustomerOrderMsterSerializer, SaleAdditionalChargeSerializer
from src.customer_order.models import OrderMain


class SaleMainView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleViewPermission]
    queryset = SaleMain.objects.all()
    serializer_class = SaleMainSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_no", "customer__first_name"]
    filter_fields = ["customer", "sale_type"]
    ordering_fields = ["id", "sale_no"]


class SaleMainSaleView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleViewPermission]
    queryset = SaleMain.objects.filter(sale_type=1)
    serializer_class = SaleMainSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_no", "customer__first_name"]
    filter_fields = ["customer", "sale_type"]
    ordering_fields = ["id", "sale_no"]


class SaleMainReturnView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleReturnViewPermission]
    queryset = SaleMain.objects.filter(sale_type=2)
    serializer_class = SaleMainSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_no", "customer__first_name"]
    filter_fields = ["customer", "sale_type"]
    ordering_fields = ["id", "sale_no"]


class SaleDetailView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleDetailViewPermission]
    queryset = SaleDetail.objects.all()
    serializer_class = SaleDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["item", "sale_main__customer"]
    filter_fields = ["sale_main", "item", "item__item_category"]
    ordering_fields = ["id", "sale_main", "sale_main__sale_no"]


class SalePaymentDetailView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleDetailViewPermission]
    queryset = SalePaymentDetail.objects.all()
    serializer_class = SalePaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_main__customer"]
    filter_fields = ["sale_main", "id", "payment_mode"]
    ordering_fields = ["id"]


class SaleAdditionalChargeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleDetailViewPermission]
    queryset = SaleAdditionalCharge.objects.all()
    serializer_class = SaleAdditionalChargeSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["remarks"]
    filter_fields = ["sale_main", "id", "charge_type"]
    ordering_fields = ["id", 'charge_type', 'sale_main', 'amount']


class SaleDetailForReturnViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [SaleViewPermission]
    queryset = SaleDetail.objects.filter(ref_sale_detail__isnull=True)
    serializer_class = SaleDetailForSaleReturnSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["item", "customer"]
    filter_fields = ["sale_main", "item", "item__item_category"]
    ordering_fields = ["id", "sale_main"]


class SaveSaleView(viewsets.ModelViewSet):
    permission_classes = [SaleSavePermission]
    queryset = SaleMain.objects.all()
    serializer_class = SaveSaleMainSerializer

    def list(self, request, **kwargs):
        data = {}
        customer = Customer.objects.filter(active=True)
        customer_serializer = CustomerSerializer(customer, many=True)
        discount_scheme = DiscountScheme.objects.filter(active=True)
        discount_scheme_serializer = DiscountSchemeSerializer(
            discount_scheme, many=True)
        additional_charge = AdditionalChargeType.objects.filter(active=True)
        additional_charge_serializer = AdditionalChargeTypeSerializer(
            additional_charge, many=True)
        payment_modes = PaymentMode.objects.filter(active=True)
        payment_mode_serializer = PaymentModeSerializer(
            payment_modes, many=True)
        data["payment_modes"] = payment_mode_serializer.data
        data["customers"] = customer_serializer.data
        data["discount_schemes"] = discount_scheme_serializer.data
        data["additional_charges"] = additional_charge_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if OrganizationSetup.objects.first() is None:
            return Response({'organization setup': 'Please insert Organization setup before making any sale'})

        try:
            sale_details = request.data["sale_details"]
        except KeyError:
            return Response({"key_error": "Provide sale_details"}, status=status.HTTP_400_BAD_REQUEST)

        '''Validation for same table in order and sale'''
        if request.data["ref_order_main"] is not None:
            order_main = OrderMain.objects.get(id=request.data["ref_order_main"])
            order_table_id = order_main.table.id
            sale_table_id = request.data['table']
            if order_table_id != sale_table_id:
                return Response({'Table': f'table id:{order_table_id} in order not equal to table id:{sale_table_id}'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'ref_order_main': 'Please Provide ref_order_main for Sale'}, status=status.HTTP_400_BAD_REQUEST)
        for sale_detail in sale_details:
            # check the type of item being sold
            item_id = sale_detail['item']
            item = Item.objects.get(id=item_id)
            if item.item_type == 3:
                try:
                    ref_purchase_detail = int(sale_detail["ref_purchase_detail"])
                except KeyError:
                    return Response({"key_error": f"Provide ref_purchase_detail for {item.name}"}, status=status.HTTP_400_BAD_REQUEST)
                stock_data = stock.get_remaining_qty_of_purchase(ref_purchase_detail)
                qty = Decimal(sale_detail["qty"])
                if stock_data < qty:
                    return Response("Given qty ({}) greater than stock qty ({})".format(qty, stock_data),
                                    status=status.HTTP_400_BAD_REQUEST)
        request.data["sale_no"] = generate_sale_no(1)
        request.data["sale_type"] = 1

        serializer = SaveSaleMainSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            order_main = request.data["ref_order_main"]
            order_main_object = OrderMain.objects.get(id=order_main)
            order_serializer = UpdateCustomerOrderMsterSerializer(
                order_main_object, data={"status": 2}, partial=True)
            if order_serializer.is_valid(raise_exception=True):
                order_serializer.save()
                # check if the order was on Table
                if order_main_object.order_type == 1:
                    # updating table to vacant state
                    table = order_main_object.table
                    table.no_of_attendant = 0
                    table.customer = None
                    table.status = 2
                    table.save()
            else:
                return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # send data to IRD
            sale_main_id = serializer.data['id']
            ird_thread = threading.Thread(target=save_data_to_ird, args=(sale_main_id, request), kwargs={})
            ird_thread.setDaemon = True
            ird_thread.start()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def save_data_to_ird(sale_main_id, request):
    api_url = "http://103.1.92.174:9050/api/bill"
    with connection.cursor() as cursor:
        try:
            cursor.execute(f"set search_path to {tenant_schema_from_request(request)}")
            sale_main = SaleMain.objects.get(id=sale_main_id)
            customer = sale_main.customer
            organization_setup = OrganizationSetup.objects.first()
            fiscal_year = str(get_fiscal_year_code_bs()).replace("/", ".")
            customer_name = str(f"{customer.first_name} {customer.middle_name} {customer.last_name}").replace("  ", " ")
            data = {
                "username": "Test_CBMS",
                "password": "test@321",
                "seller_pan": str(organization_setup.pan_no),  # from organization setup
                "buyer_pan": str(customer.pan_vat_no),  # from customer
                "fiscal_year": fiscal_year,  # get_fiscal year function e.g 77.78
                "buyer_name": customer_name,  # from customer first name, middle name, last name
                "invoice_number": sale_main.sale_no,  # Sale no
                "invoice_date": sale_main.created_date_bs,  # created_data_bs of sale
                "total_sale": float(sale_main.sub_total),  # Sub Total of sale
                "taxable_sale_vat": float(sale_main.total_tax),  # Tax amount of sale
                "vat": "0",  # vat of sale
                "excisable_amount": 0,  # zero 0
                "excise": 0,  # zero 0
                "taxable_sale_hst": 0,  # zero 0
                "hst": 0,  # zero 0
                "amount_for_esf": 0,  # zero 0
                "esf": 0,  # zero 0
                "export_sales": 0,  # zero 0
                "tax_exempted_sale": 0,  # zero 0
                "isrealtime": True,
                "datetimeClient": str(timezone.now().strftime("%Y-%m-%d %H:%M:%S"))  # date('Y-m-d h:i:s');

            }
        except:
            ird_update = IRDUploadLog.objects.create(sale_main=sale_main, status_code=504,
                                                     response_message="Exception while sending IRD LOG",
                                                     created_by=sale_main.created_by,
                                                     created_date_bs=sale_main.created_date_ad)
            ird_update.save()

        try:
            response = requests.post(api_url, data=data)

        except:
            ird_update = IRDUploadLog.objects.create(sale_main=sale_main, status_code=504,
                                                     response_message="Server time out",
                                                     created_by=sale_main.created_by,
                                                     created_date_bs=sale_main.created_date_ad)
            ird_update.save()
            print("server not Found")
        else:
            if response.status_code == "200":
                ird_update = IRDUploadLog.objects.create(sale_main=sale_main, status_code=response.status_code,
                                                         response_message="Log saved to IRD",
                                                         created_by=sale_main.created_by,
                                                         created_date_bs=sale_main.created_date_ad)
                ird_update.save()
                sale_main.real_time_upload = True
                sale_main.synced_with_ird = True
                sale_main.save()
            else:
                ird_update = IRDUploadLog.objects.create(sale_main=sale_main, status_code=response.status_code,
                                                         response_message="Log Not saved to IRD",
                                                         created_by=sale_main.created_by,
                                                         created_date_bs=sale_main.created_date_ad)
                ird_update.save()


class ReturnSaleView(viewsets.ModelViewSet):
    permission_classes = [SaleReturnPermission]
    queryset = SaleMain.objects.all()
    serializer_class = SaveSaleMainSerializer

    def list(self, request, **kwargs):
        data = {}
        customer = Customer.objects.filter(active=True)
        customer_serializer = CustomerSerializer(customer, many=True)
        discount_scheme = DiscountScheme.objects.filter(active=True)
        discount_scheme_serializer = DiscountSchemeSerializer(
            discount_scheme, many=True)
        additional_charge = AdditionalChargeType.objects.filter(active=True)
        additional_charge_serializer = AdditionalChargeTypeSerializer(
            additional_charge, many=True)
        payment_modes = PaymentMode.objects.filter(active=True)
        payment_mode_serializer = PaymentModeSerializer(
            payment_modes, many=True)
        data["payment_modes"] = payment_mode_serializer.data
        data["customers"] = customer_serializer.data
        data["discount_schemes"] = discount_scheme_serializer.data
        data["additional_charges"] = additional_charge_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        try:
            sale_details = request.data["sale_details"]
        except KeyError:
            return Response({"key_error": "Provide sale_details"}, status=status.HTTP_400_BAD_REQUEST)
        for sale in sale_details:
            ref_id_sale = int(sale["ref_sale_detail"])
            total_quantity = SaleDetail.objects.values_list(
                "qty", flat=True).get(pk=ref_id_sale)
            return_quantity = sum(SaleDetail.objects.filter(ref_sale_detail=ref_id_sale)
                                  .values_list("qty", flat=True)) + Decimal(sale["qty"])

            if total_quantity < return_quantity:
                return Response("Return items ({}) more than sale items({})".format(return_quantity, total_quantity),
                                status=status.HTTP_400_BAD_REQUEST)

        request.data["sale_no"] = generate_sale_no(2)
        request.data["sale_type"] = 2
        serializer = SaveSaleMainSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SalePrintLogViewset(viewsets.ModelViewSet):
    permission_classes = [SalePrintLogPermission]
    queryset = SalePrintLog.objects.all()
    serializer_class = SalePrintLogSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ["sale_main"]
    filter_fields = ["id"]
    ordering_fields = ["id"]

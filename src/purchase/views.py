# from custom
from utils.functions import stock

import django_filters
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from django.db import transaction

from decimal import Decimal
from django_filters import rest_framework as filters

# imported serializers
from .serializers import PurchaseOrderMainSerializer, PurchaseOrderDetailSerializer
from .serializers import PurchaseMainSerializer, PurchaseDetailSerializer
from .serializers import SavePurchaseOrderMainSerializer, SavePurchaseMainSerializer
from .serializers import GetPurchaseOrderMainSerializer, PurchasePaymentDetailSerializer, \
    PurchaseAdditionalChargeSerializer
from src.item.serializers import ItemSerializer
from src.supplier.serializers import SupplierSerializer
from src.core_app.serializers import DiscountSchemeSerializer, AdditionalChargeTypeSerializer, PaymentModeSerializer
# imported models
from .models import PurchaseOrderMain, PurchaseOrderDetail, PurchasePaymentDetail, PurchaseAdditionalCharge
from .models import PurchaseMain, PurchaseDetail
from src.item.models import Item
from src.supplier.models import Supplier
from src.core_app.models import DiscountScheme, AdditionalChargeType, PaymentMode

# custom files
from .purchase_unique_id_generator import generate_order_no, generate_purchase_no
from .purchase_permissions import PurchaseOrderViewPermission, PurchaseViewPermission, PurchaseOrderSavePermission, \
    PurchaseOrderApprovePermission, PurchaseDirectPermission, PurchaseReturnPermission, PurchaseAdditionPermission, \
    PurchaseOrderCancelPermission, PurchaseOrderApprovedViewPermission, PurchaseReturnedViewPermission, \
    PurchaseOrderCancelledViewPermission, PurchaseOrderDetailViewPermission, \
    PurchaseDetailViewPermission

'''------------------------------------- get Purchase Order views ---------------------------------------------- '''


# custom filter for bank model
class FilterForGetOrders(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseOrderMain
        fields = ['order_no', 'created_by__user_name', 'created_date_ad', 'order_type', 'supplier']


class GetUnAppUnCanPurchaseOrderMainView(viewsets.ModelViewSet):
    queryset = PurchaseOrderMain.objects.all()
    serializer_class = GetPurchaseOrderMainSerializer
    http_method_names = ['get', 'head']
    filter_class = FilterForGetOrders
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__first_name', 'supplier__last_name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks']
    ordering_fields = ['id', 'order_no']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = [PurchaseOrderViewPermission]
        elif self.action == 'pending':
            self.permission_classes = [PurchaseOrderViewPermission]
        elif self.action == 'cancelled':
            self.permission_classes = [PurchaseOrderCancelledViewPermission]
        elif self.action == 'approved':
            self.permission_classes = [PurchaseOrderApprovedViewPermission]
        return super(self.__class__, self).get_permissions()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(PurchaseOrderMain.objects.filter(ref_purchase_order__isnull=True))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request, *args, **kwargs):
        id_list = PurchaseOrderMain.objects.filter(order_type__gt=1).values_list('ref_purchase_order', flat=True)
        queryset = self.filter_queryset(PurchaseOrderMain.objects.filter(order_type=1).exclude(id__in=id_list))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def cancelled(self, request, *args, **kwargs):
        queryset = self.filter_queryset(PurchaseOrderMain.objects.filter(order_type=2))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def approved(self, request, *args, **kwargs):
        queryset = self.filter_queryset(PurchaseOrderMain.objects.filter(order_type=3))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PurchaseOrderMainViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderViewPermission]
    queryset = PurchaseOrderMain.objects.all()
    serializer_class = PurchaseOrderMainSerializer
    http_method_names = ['get', 'head']
    filter_class = FilterForGetOrders
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['order_no', 'supplier__first_name', 'supplier__last_name',
                     'created_by__user_name', 'discount_scheme__name', 'order_type', 'remarks']
    ordering_fields = ['id', 'order_no']


class PurchaseOrderDetailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseOrderDetailViewPermission]
    queryset = PurchaseOrderDetail.objects.all()
    serializer_class = PurchaseOrderDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['item', 'item_category']
    ordering_fields = ['id']
    filter_fields = ['id', 'item', 'purchase_order', 'ref_purchase_order_detail']


'''---------------------------------------------- Get views for Purchase ----------------------------------------------'''


class PurchaseMainViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseViewPermission]
    queryset = PurchaseMain.objects.all()
    serializer_class = PurchaseMainSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'bill_no', 'chalan_no', 'supplier__first_name',
                     "supplier__middle_name", 'supplier__last_name']
    ordering_fields = ['id', 'created_date_ad__date', 'pay_type']
    filter_fields = ['id', 'created_date_ad', 'created_date_bs', 'pay_type', 'purchase_type', 'supplier']


class PurchaseMainPurchaseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseViewPermission]
    queryset = PurchaseMain.objects.filter(purchase_type=1)
    serializer_class = PurchaseMainSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'bill_no', 'chalan_no', 'supplier__first_name',
                     "supplier__middle_name", 'supplier__last_name']
    ordering_fields = ['id', 'created_date_ad__date', 'pay_type', 'purchase_no']
    filter_fields = ['id', 'created_date_ad', 'created_date_bs', 'pay_type', 'purchase_type', 'supplier']


class PurchaseMainReturnedViewSet(viewsets.ModelViewSet):
    permission_classes = [PurchaseReturnedViewPermission]
    queryset = PurchaseMain.objects.filter(purchase_type=2)
    serializer_class = PurchaseMainSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no', 'bill_no', 'chalan_no', 'supplier__first_name',
                     "supplier__middle_name", 'supplier__last_name']
    ordering_fields = ['id', 'created_date_ad__date', 'pay_type', 'purchase_no']
    filter_fields = ['id', 'created_date_ad', 'created_date_bs', 'pay_type', 'purchase_type', 'supplier']


class PurchaseDetailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseDetailViewPermission]
    queryset = PurchaseDetail.objects.all()
    serializer_class = PurchaseDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['id', 'item__name', 'purchase__purchase_no', 'batch_no']
    ordering_fields = ['id']
    filter_fields = ['purchase']


class PurchasePaymentDetailFilter(filters.FilterSet):
    purchase_order_main = filters.NumberFilter(field_name="purchase_main__ref_purchase_order")

    class Meta:
        model = PurchasePaymentDetail
        fields = ['purchase_main', 'id', 'payment_mode', 'purchase_order_main']


class PurchasePaymentDetailsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseDetailViewPermission]
    queryset = PurchasePaymentDetail.objects.all()
    serializer_class = PurchasePaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['remarks']
    ordering_fields = ['id', 'purchase_main', 'payment_mode', 'amount']
    filterset_class = PurchasePaymentDetailFilter


class PurchaseAdditionalChargeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PurchaseDetailViewPermission]
    queryset = PurchaseAdditionalCharge.objects.all()
    serializer_class = PurchaseAdditionalChargeSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['remarks']
    ordering_fields = ['id', 'charge_type', 'purchase_main', 'amount']
    filter_fields = ['purchase_main', 'id', 'charge_type']


'''----------------------- Views to save purchase order and purchase-------------------------------'''


class SavePurchaseOrderView(viewsets.ModelViewSet):
    permission_classes = [PurchaseOrderSavePermission]
    queryset = PurchaseOrderMain.objects.all()
    serializer_class = SavePurchaseOrderMainSerializer

    def list(self, request, **kwargs):
        data = {}
        items = Item.objects.filter(active=True).order_by('name')
        item_serializer = ItemSerializer(items, many=True)
        suppliers = Supplier.objects.filter(active=True).order_by('first_name')
        suppliers_serializer = SupplierSerializer(suppliers, many=True)
        discount_scheme = DiscountScheme.objects.filter(active=True).order_by('name')
        discount_scheme_serializer = DiscountSchemeSerializer(discount_scheme, many=True)
        payment_modes = PaymentMode.objects.filter(active=True).order_by('name')
        payment_mode_serializer = PaymentModeSerializer(payment_modes, many=True)
        data['payment_modes'] = payment_mode_serializer.data
        data['items'] = item_serializer.data
        data['suppliers'] = suppliers_serializer.data
        data['discount_schemes'] = discount_scheme_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, **kwargs):
        print(request.data)
        request.data['order_type'] = 1
        request.data['order_no'] = generate_order_no(1)

        serializer = SavePurchaseOrderMainSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CancelPurchaseOrderView(viewsets.ModelViewSet):
    permission_classes = [PurchaseOrderCancelPermission]
    queryset = PurchaseOrderMain.objects.all()
    serializer_class = SavePurchaseOrderMainSerializer
    http_method_names = ['get', 'head', 'post']

    def list(self, request, **kwargs):
        data = {}
        items = Item.objects.filter(active=True).order_by('name')
        item_serializer = ItemSerializer(items, many=True)
        suppliers = Supplier.objects.filter(active=True).order_by('first_name')
        suppliers_serializer = SupplierSerializer(suppliers, many=True)
        discount_scheme = DiscountScheme.objects.filter(active=True).order_by('name')
        discount_scheme_serializer = DiscountSchemeSerializer(discount_scheme, many=True)
        data['items'] = item_serializer.data
        data['suppliers'] = suppliers_serializer.data
        data['discount_schemes'] = discount_scheme_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, **kwargs):

        try:
            ref_id = request.data['ref_purchase_order']
        except KeyError:
            return Response('please provide ref_purchase_order', status=status.HTTP_400_BAD_REQUEST)

        if PurchaseOrderMain.objects.filter(ref_purchase_order=ref_id).exists():
            return Response('Order already Approved or cancelled', status=status.HTTP_400_BAD_REQUEST)

        purchase_details = request.data['purchase_order_details']
        ref_purchase_details = []
        for purchase_detail in purchase_details:
            try:
                ref_purchase_details.append(purchase_detail['ref_purchase_order_detail'])
            except KeyError:
                return Response('please provide ref_purchase_order_detail', status=status.HTTP_400_BAD_REQUEST)

        # validation for all purchase order details present in cancel purchase order data
        order_details_id = PurchaseOrderDetail.objects.filter(purchase_order=ref_id).values_list('id', flat=True)
        if len(ref_purchase_details) != len(order_details_id):
            return Response({'object_error': 'Number of purchse order details object  you '
                                             'provided {} not match : available {}'.format(ref_purchase_details,
                                                                                           order_details_id)})
        for ref_purchase in ref_purchase_details:
            if ref_purchase not in order_details_id:
                return Response({'not_exist': 'A Purchase order detail not present in cancel order operation, Please'
                                              'provide all details of main being cancelled'})

        request.data['order_no'] = generate_order_no(2)
        request.data['order_type'] = 2
        serializer = SavePurchaseOrderMainSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ApprovePurchaseOrderView(viewsets.ModelViewSet):
    permission_classes = [PurchaseOrderApprovePermission]
    http_method_names = ['get', 'head', 'post']
    serializer_class = SavePurchaseMainSerializer
    queryset = PurchaseMain.objects.all()

    def list(self, request, **kwargs):
        data = {}
        suppliers = Supplier.objects.filter(active=True).order_by('first_name')
        suppliers_serializer = SupplierSerializer(suppliers, many=True)
        discount_scheme = DiscountScheme.objects.filter(active=True).order_by('name')
        discount_scheme_serializer = DiscountSchemeSerializer(discount_scheme, many=True)
        additional_charge = AdditionalChargeType.objects.filter(active=True).order_by('name')
        additional_charge_serializer = AdditionalChargeTypeSerializer(additional_charge, many=True)
        items = Item.objects.filter(active=True).order_by('name')
        item_serializer = ItemSerializer(items, many=True)
        payment_modes = PaymentMode.objects.filter(active=True).order_by('name')
        payment_mode_serializer = PaymentModeSerializer(payment_modes, many=True)
        data['payment_modes'] = payment_mode_serializer.data
        data['items'] = item_serializer.data
        data['suppliers'] = suppliers_serializer.data
        data['discount_schemes'] = discount_scheme_serializer.data
        data['additional_charges'] = additional_charge_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Key validation fro purchase order main
        try:
            purchase_order_main = request.data.pop('purchase_order_main')
        except KeyError:

            return Response('Provide purchase Order Data in purchase_order_main key',
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            purchase_order_main['ref_purchase_order']
        except KeyError:
            return Response('Provide ref_purchase_order in purchase_order_main key ',
                            status=status.HTTP_400_BAD_REQUEST)
        # for purchase_order_detail in purchase_order_main['purchase_order_details']:
        #     try:
        #         purchase_order_detail['ref_purchase_order_detail']
        #     except ValueError:
        #         return Response('Provide ref_purchase_order_detail purchase_order_main key',
        #                         status=status.HTTP_400_BAD_REQUEST)

        # Key validation fro purchase main
        try:
            purchase_main = request.data.pop('purchase_main')
        except KeyError:
            return Response('Provide purchase Data in purchase_main key')
        try:
            purchase_main['ref_purchase_order']
        except KeyError:
            return Response('Provide ref_purchase_order purchase_main key', status=status.HTTP_400_BAD_REQUEST)

        """***********************"""
        purchase_details = purchase_main['purchase_details'].copy()
        for purchase_detail in purchase_details:
            try:
                if purchase_detail['expiry_date_ad'] == "":
                    purchase_detail['expiry_date_ad'] = None
            except KeyError:
                return Response({"key_error": "provide expiry_date_ad key"},
                                status=status.HTTP_400_BAD_REQUEST)

            if "free_qty" in purchase_detail:
                free_purchase = {
                    "item": purchase_detail["item"],
                    "item_category": purchase_detail["item"],
                    "purchase_cost": purchase_detail["item"],
                    "sale_cost": purchase_detail["item"],
                    "taxable": purchase_detail["taxable"],
                    "tax_rate": purchase_detail["tax_rate"],
                    "tax_amount": purchase_detail["tax_amount"],
                    "qty": purchase_detail["free_qty"],
                    "discountable": True,
                    "expirable": purchase_detail["expirable"],
                    "discount_rate": "100",
                    "discount_amount": (Decimal(purchase_detail["purchase_cost"]) * Decimal(
                        purchase_detail["free_qty"])) + purchase_detail['tax_amount'],
                    "gross_amount": (Decimal(purchase_detail["purchase_cost"]) * Decimal(
                        purchase_detail["free_qty"])) + purchase_detail['tax_amount'],
                    "net_amount": Decimal("0.00"),
                    "expiry_date_ad": purchase_detail["expiry_date_ad"],
                    "expiry_date_bs": purchase_detail["expiry_date_bs"],
                    "batch_no": purchase_detail["batch_no"],
                }
                purchase_main['purchase_details'].append(free_purchase)
        """************************************"""

        # validation for date time fields with blank values
        try:
            purchase_main['bill_no']
            if purchase_main['bill_date_ad'] == "":
                purchase_main['bill_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide bill_no and bill_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            purchase_main['chalan_no']
            if purchase_main['due_date_ad'] == "":
                purchase_main['due_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide chalan_no and due_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)

        purchase_order_main_ref_id = purchase_order_main['ref_purchase_order']
        if PurchaseOrderMain.objects.filter(ref_purchase_order=purchase_order_main_ref_id).exists():
            return Response('Order already Approved or cancelled', status=status.HTTP_400_BAD_REQUEST)

        # insert data for  purchase order main
        purchase_order_main['order_no'] = generate_order_no(3)
        purchase_order_main['order_type'] = 3
        purchase_order_serializer = SavePurchaseOrderMainSerializer(data=purchase_order_main,
                                                                    context={'request': request})

        # insert data for purchase main
        purchase_main['purchase_no'] = generate_purchase_no(1)
        purchase_main['purchase_type'] = 1
        purchase_serializer = SavePurchaseMainSerializer(data=purchase_main, context={'request': request})
        # saving both fields data
        if purchase_serializer.is_valid(raise_exception=True):
            if purchase_order_serializer.is_valid(raise_exception=True):
                purchase_serializer.save()
                purchase_order_serializer.save()
                return Response(purchase_order_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(purchase_order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(purchase_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class DirectApprovePurchaseView(viewsets.ModelViewSet):
    permission_classes = [PurchaseDirectPermission]
    serializer_class = SavePurchaseMainSerializer
    http_method_names = ['post', 'head', 'get']
    queryset = PurchaseMain.objects.all()

    def list(self, request, **kwargs):
        data = {}

        suppliers = Supplier.objects.filter(active=True).order_by('first_name')
        suppliers_serializer = SupplierSerializer(suppliers, many=True)
        discount_scheme = DiscountScheme.objects.filter(active=True).order_by('name')
        discount_scheme_serializer = DiscountSchemeSerializer(discount_scheme, many=True)
        additional_charge = AdditionalChargeType.objects.filter(active=True).order_by('name')
        additional_charge_serializer = AdditionalChargeTypeSerializer(additional_charge, many=True)
        items = Item.objects.filter(active=True).order_by('name')
        item_serializer = ItemSerializer(items, many=True)
        payment_modes = PaymentMode.objects.filter(active=True).order_by('name')
        payment_mode_serializer = PaymentModeSerializer(payment_modes, many=True)
        data['payment_modes'] = payment_mode_serializer.data
        data['items'] = item_serializer.data
        data['suppliers'] = suppliers_serializer.data
        data['discount_schemes'] = discount_scheme_serializer.data
        data['additional_charges'] = additional_charge_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # validation for Date fields being empty
        purchase_details = request.data['purchase_details'].copy()
        for purchase_detail in purchase_details:
            try:
                if purchase_detail['expiry_date_ad'] == "":
                    purchase_detail['expiry_date_ad'] = None
            except KeyError:
                return Response({"key_error": "provide expiry_date_ad key"},
                                status=status.HTTP_400_BAD_REQUEST)

            if "free_qty" in purchase_detail:
                free_purchase = {
                    "item": purchase_detail["item"],
                    "item_category": purchase_detail["item"],
                    "purchase_cost": purchase_detail["item"],
                    "sale_cost": purchase_detail["item"],
                    "taxable": purchase_detail["taxable"],
                    "tax_rate": purchase_detail["tax_rate"],
                    "tax_amount": purchase_detail["tax_amount"],
                    "qty": purchase_detail["free_qty"],
                    "discountable": True,
                    "expirable": purchase_detail["expirable"],
                    "discount_rate": "100",
                    "discount_amount": (Decimal(purchase_detail["purchase_cost"]) * Decimal(
                        purchase_detail["free_qty"])) + purchase_detail['tax_amount'],
                    "gross_amount": (Decimal(purchase_detail["purchase_cost"]) * Decimal(purchase_detail["free_qty"])) +
                                    purchase_detail['tax_amount'],
                    "net_amount": Decimal("0.00"),
                    "expiry_date_ad": purchase_detail["expiry_date_ad"],
                    "expiry_date_bs": purchase_detail["expiry_date_bs"],
                    "batch_no": purchase_detail["batch_no"],
                }
                request.data['purchase_details'].append(free_purchase)

        # validation for date time fields with blank values

        try:
            request.data['bill_no']
            if request.data['bill_date_ad'] == "":
                request.data['bill_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide bill_no and bill_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            request.data['chalan_no']
            if request.data['due_date_ad'] == "":
                request.data['due_date_ad'] = None
        except KeyError:
            return Response({'key_error': 'please provide chalan_no and due_date_ad Keys'},
                            status=status.HTTP_400_BAD_REQUEST)

        # saving fields data
        request.data['purchase_no'] = generate_purchase_no(1)
        request.data['purchase_type'] = 1
        serializer = SavePurchaseMainSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ReturnPurchaseView(viewsets.ModelViewSet):
    permission_classes = [PurchaseReturnPermission]
    serializer_class = SavePurchaseMainSerializer
    http_method_names = ['post', 'head', 'get']
    queryset = PurchaseMain.objects.all()

    def list(self, request, **kwargs):
        data = {}
        suppliers = Supplier.objects.filter(active=True).order_by('first_name')
        suppliers_serializer = SupplierSerializer(suppliers, many=True)
        discount_scheme = DiscountScheme.objects.filter(active=True).order_by('name')
        discount_scheme_serializer = DiscountSchemeSerializer(discount_scheme, many=True)
        additional_charge = AdditionalChargeType.objects.filter(active=True).order_by('name')
        additional_charge_serializer = AdditionalChargeTypeSerializer(additional_charge, many=True)
        payment_modes = PaymentMode.objects.filter(active=True).order_by('name')
        payment_mode_serializer = PaymentModeSerializer(payment_modes, many=True)
        data['payment_modes'] = payment_mode_serializer.data
        data['suppliers'] = suppliers_serializer.data
        data['discount_schemes'] = discount_scheme_serializer.data
        data['additional_charges'] = additional_charge_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        purchase_detail = request.data['purchase_details']
        for detail in purchase_detail:
            ref_purchase_detail = int(detail['ref_purchase_detail'])
            remaining_quantity = stock.get_remaining_qty_of_purchase(ref_purchase_detail)
            qty = Decimal(detail['qty'])
            if remaining_quantity < qty:
                return Response("Invalid return qty for item {} :remaining quantity {}".format(detail['item_name'],
                                                                                               remaining_quantity),
                                status=status.HTTP_403_FORBIDDEN)

        request.data['purchase_no'] = generate_purchase_no(2)
        request.data['purchase_type'] = 2
        serializer = SavePurchaseMainSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class PurchaseAdditionView(viewsets.ModelViewSet):
    serializer_class = SavePurchaseMainSerializer
    http_method_names = ['post', 'head']
    queryset = PurchaseMain.objects.all()

    def list(self, request, **kwargs):
        data = {}
        suppliers = Supplier.objects.filter(active=True).order_by('first_name')
        suppliers_serializer = SupplierSerializer(suppliers, many=True)
        discount_scheme = DiscountScheme.objects.filter(active=True).order_by('name')
        discount_scheme_serializer = DiscountSchemeSerializer(discount_scheme, many=True)
        additional_charge = AdditionalChargeType.objects.filter(active=True).order_by('name')
        additional_charge_serializer = AdditionalChargeTypeSerializer(additional_charge, many=True)
        items = Item.objects.filter(active=True).order_by('name')
        item_serializer = ItemSerializer(items, many=True)
        data['items'] = item_serializer.data
        data['suppliers'] = suppliers_serializer.data
        data['discount_schemes'] = discount_scheme_serializer.data
        data['additional_charges'] = additional_charge_serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # validation for Date fields being empty
        for purchase_detail in request.data['purchase_details']:
            try:
                if purchase_detail['expiry_date_ad'] == "":
                    purchase_detail['expiry_date_ad'] = None
            except KeyError:
                return Response({"key_error": "provide expiry_date_ad key"},
                                status=status.HTTP_400_BAD_REQUEST)

            # validation for date time fields with blank values
            # pay_type (1) = CASH
            if request.data['pay_type'] == 1:
                try:
                    request.data['bill_no']
                    if request.data['bill_date_ad'] == "":
                        request.data['bill_date_ad'] = None
                except KeyError:
                    return Response({'key_error': 'please provide bill_no and bill_date_ad Keys'},
                                    status=status.HTTP_400_BAD_REQUEST)
            # pay_type (2) = CREDIT
            if request.data['pay_type'] == 2:
                try:
                    request.data['chalan_no']
                    if request.data['due_date_ad'] == "":
                        request.data['due_date_ad'] = None
                except KeyError:
                    return Response({'key_error': 'please provide chalan_no and due_date_ad Keys'},
                                    status=status.HTTP_400_BAD_REQUEST)

        # saving fields data
        request.data['purchase_no'] = generate_purchase_no(3)
        request.data['purchase_type'] = 3
        serializer = SavePurchaseMainSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        return Response({"method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

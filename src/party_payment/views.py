from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from src.supplier.models import Supplier
from src.supplier.serializers import SupplierSerializer
from decimal import Decimal
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from django_filters import DateFromToRangeFilter
from django.db import transaction
from src.purchase.models import PurchaseMain


from .serializers import PartyClearanceMainSerializer, PartyPaymentDetailSerializer, PurchaseCreditSerializer
from .serializers import SavePartyPaymentDetailSerializer, SavePartyClearanceSerializer

from .models import PartyClearance,PartyPaymentDetail
from utils.functions.party_payment import get_purchase_credit_detail

# Custom
from .reciept_unique_id_generator import get_receipt_no
from .party_payment_permissions import PartyClearanceSavePermission, PartyClearanceViewPermission

# Create your views here.
class RangeFilterForPartyClearance(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PartyClearance
        fields = '__all__'


class PartyClearanceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyClearanceViewPermission]
    queryset = PartyClearance.objects.all()
    serializer_class = PartyClearanceMainSerializer
    filter_class = RangeFilterForPartyClearance
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    common_filter = "__all__"
    search_filter = "__all__"
    search_fields = search_filter
    ordering_fields = common_filter
    filterset_fields = common_filter


class PartyPaymentDetailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyClearanceViewPermission]
    queryset = PartyPaymentDetail.objects.all()
    serializer_class = PartyPaymentDetailSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_fields = ['id','party_clearance__purchase_main']
    ordering_fields = ['party_clearance', 'id']


class PartyClearanceSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyClearanceViewPermission]
    queryset = PartyClearance.objects.all()
    serializer_class = SavePartyClearanceSerializer
    filter_class = RangeFilterForPartyClearance
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)


class FilterForCreditReportPurchaseMain(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = PurchaseMain
        fields = ['id', 'purchase_no', 'created_by', 'created_date_ad', 'pay_type', 'supplier']


class GetPartyInvoice(viewsets.ReadOnlyModelViewSet):
    permission_classes = [PartyClearanceViewPermission]
    queryset = PurchaseMain.objects.filter(pay_type=2)
    serializer_class = PurchaseCreditSerializer
    filter_class = FilterForCreditReportPurchaseMain
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['purchase_no']
    ordering_fields = ['purchase_id', 'created_date_ad']

    @action(detail=False, methods=['GET'])
    def suppliers(self, request):
        data = get_purchase_credit_detail()
        id_list = data.values_list('supplier', flat=True)
        # converting a list into set for removing repeated values
        supplier_id_list = set(id_list)
        suppliers = Supplier.objects.filter(id__in=supplier_id_list)
        suppliers_serializer = SupplierSerializer(suppliers, many=True)
        return Response(suppliers_serializer.data, status=status.HTTP_200_OK)


class SavePartyClearanceViewSet(viewsets.ModelViewSet):
    permission_classes = [PartyClearanceSavePermission]
    queryset = PartyClearance.objects.all()
    serializer_class = SavePartyClearanceSerializer

    @transaction.atomic
    def create(self, request):
        quantize_places = Decimal(10) ** -2

        try:
            supplier_id = request.data.pop('supplier_id')
            purchase_main_id_list = request.data.pop('purchase_mains')
            remarks = request.data.pop('remarks')
            payment_details = request.data.pop('payment_details')
        except KeyError:
            return Response("Please provide supplier_id, purchase_mains, remarks and payment_details values",
                            status=status.HTTP_400_BAD_REQUEST)

        # calculating total amount
        total_paying_amount = Decimal('0.00')
        for detail in payment_details:
            amount = Decimal(str(detail['amount']))
            total_paying_amount = total_paying_amount + amount

        total_due_amount = Decimal('0.00')
        for purchase_id in purchase_main_id_list:
            # Get due_amount of the given supplier
            data = get_purchase_credit_detail(supplier=supplier_id, purchase_main=purchase_id)
            if data[0]['due_amount'] <= 0:
                return Response('This invoice id ({}) has zero due_amount please unselect it'.format(purchase_id))
            total_due_amount += data[0]['due_amount']

        total_due_amount = total_due_amount.quantize(quantize_places)
        total_paying_amount = total_paying_amount.quantize(quantize_places)

        if total_paying_amount > total_due_amount:
            return Response("Your paying amount is {}, due amount is {}. Payment amount must be less than due amount".format(total_paying_amount, total_due_amount),
                            status=status.HTTP_400_BAD_REQUEST)
        response_data = []
        for purchase_id in purchase_main_id_list:

            # check if payment_details have any amount left
            total_sum = Decimal('0.00')
            for detail in payment_details:
                total_sum = total_sum + Decimal(str(detail['amount']))
            if total_sum <= 0:
                break

            # Get due_amount for given supplier
            data = get_purchase_credit_detail(supplier=supplier_id, purchase_main=purchase_id)
            due_amount = data[0]['due_amount']
            party_payment_details = []

            # calcaulate credit_payment_details
            for detail in payment_details:
                if detail['amount'] > 0:
                    if due_amount <= detail['amount']:
                        party_payment_detail = {
                            "payment_mode": detail['payment_mode'],
                            "amount": due_amount,
                            "remarks": detail['remarks']
                        }
                        detail['amount'] = detail['amount'] - due_amount
                        due_amount = 0
                        party_payment_details.append(party_payment_detail)
                        break
                    else:
                        party_payment_detail = {
                            "payment_mode": detail['payment_mode'],
                            "amount": detail['amount'],
                            "remarks": detail['remarks']
                        }
                        detail['amount'] = 0
                        due_amount = due_amount - detail['amount']
                        party_payment_details.append(party_payment_detail)
            # Calculate Total Amount for credit payment main
            total_payment = Decimal('0.00')
            for payment in party_payment_details:
                total_payment = total_payment + Decimal(str(payment['amount']))


            # 1. save Credit payment main,
            request.data['payment_type'] = 1
            
            request.data['purchase_main'] = purchase_id
            # generate unique receipt no for the CreditClearance
            request.data['receipt_no'] = get_receipt_no()
            request.data['total_amount'] = total_payment
            request.data['remarks'] = remarks

            # # 2. save Credit Payment Detail
            # credit_clearance_detail_data = [{
            #
            #     'amount': total_payment,
            # }]
            # request.data['credit_clearance_details'] = credit_clearance_detail_data

            # 3. save Credit Payment Model Detail
            request.data['party_payment_details'] = party_payment_details

            party_main_serializer = SavePartyClearanceSerializer(data=request.data, context={'request': request})

            if party_main_serializer.is_valid(raise_exception=True):
                party_main_serializer.save()
                response_data.append(party_main_serializer.data)
            else:
                return Response(
                    party_main_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return Response("method not allowed")

    def partial_update(self, request, pk=None):
        return Response("Method not allowed")

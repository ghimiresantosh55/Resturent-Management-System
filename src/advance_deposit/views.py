from rest_framework import viewsets
from .models import AdvanceDeposit
from .advance_deposite_permissions import AdvanceDepositSavePermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from .serializers import SaveAdvanceDepositSerializer


class SaveAdvancedDepositViewSet(viewsets.ModelViewSet):
    permission_classes = [AdvanceDepositSavePermission]
    queryset = AdvanceDeposit.objects.all()
    http_method_names = ['post', 'get']
    serializer_class = SaveAdvanceDepositSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['remarks']
    filter_fields = ['order_main', 'sale_main']
    ordering_fields = ['id', 'order_main', 'sale_main', 'deposit_no']

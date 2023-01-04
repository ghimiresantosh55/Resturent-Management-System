# third-party
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from rest_framework.response import Response
# imported serializers
from .serializers import CustomerSerializer

# imported models
from .models import Customer
# importing permission
from .customer_permissions import CustomerPermission
from simple_history.utils import update_change_reason


class FilterForCustomer(django_filters.FilterSet):
    date = django_filters.DateFromToRangeFilter(field_name="created_date_ad")
    first_name = django_filters.CharFilter(lookup_expr='iexact')
    address = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Customer
        fields = ['phone_no', 'active', 'id', 'pan_vat_no']


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [CustomerPermission]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filter_class = FilterForCustomer
    search_fields = ['first_name', 'address', 'id', 'pan_vat_no']
    ordering_fields = ['first_name', 'id', 'pan_vat_no']
    http_method_names = ['get', 'head', 'post', 'patch', 'option']

    # custom partial update for receiving remarks while update
    def partial_update(self, request, *args, **kwargs):
        try:
            remarks = str(request.data['remarks']).strip()
            if len(remarks) <= 0:
                return Response({'remarks': 'Please give at least one word for remarks'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'remarks': 'Please Provide remarks'}, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            update_change_reason(instance, remarks)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

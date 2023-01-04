import django_filters
from django_filters import DateFromToRangeFilter, NumberFilter
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist
# importing serializers
from .serializers import TableSerializer, BlockSerializer
from .models import Block, Table
# import models from order app
# from src.order.models import OrderMain
# filter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

class FilterForBlock(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")

    class Meta:
        model = Block
        fields = ['created_date_ad', 'date']


class BlockViewSet(viewsets.ModelViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filter_class = FilterForBlock
    search_filter = ['name', 'active', 'display_order']
    search_fields = ['name', 'active', 'display_order']
    ordering_fields = ['name', 'active', 'display_order']


class FilterForTable(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    max_capacity = NumberFilter(field_name="capacity", lookup_expr='gte')
    min_capacity = NumberFilter(field_name="capacity", lookup_expr='lte')

    class Meta:
        model = Table
        fields = ['created_date_ad', 'date', 'capacity', 'block', 'block__name', 'name']


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    filter_class = FilterForTable
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['name', 'active', 'display_order', 'block__name', 'customer__first_name']
    ordering_fields = ['name', 'active', 'display_order', 'block__name', 'customer__first_name']

    # cancel single order (update order_main and set a single order_deetail cancelled = True)
    # @action(detail=False, methods=['PATCH'])
    # def transfer(self, request, pk=None):
    # 
    #     try:
    #         main_id = request.data['order_main_id']
    #         to_table_id = request.data['table_id']
    #     except KeyError:
    #         return Response(
    #             "provide order_main_id and table_id",
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    # 
    #     if main_id == '' or to_table_id == '':
    #         return Response(
    #             "order_main id or table_id is blank",
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    # 
    #     try:
    #         order_main = OrderMain.objects.get(id=main_id)
    #         to_table = Table.objects.get(id=to_table_id)
    #         # checking the status of order_main pending(1) or not
    #         if order_main.status != 1:
    #             return Response("Order is already Cleared or Cancelled",
    #                             status=status.HTTP_400_BAD_REQUEST)
    #         # checking the status of table is vacant(1) or not
    #         if to_table.status != 1:
    #             return Response(
    #                 "The table you want to transfer to is not vacant",
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    # 
    #         from_table = order_main.table
    #         old_no_of_attendent = from_table.no_of_attendant
    #         # check there is customer in table or not
    #         if from_table.customer:
    #             old_customer = from_table.customer.id
    #         else:
    #             old_customer = ''
    #         old_status = from_table.status
    #         # updating the data of 'from table' to 'to table'"
    #         Table.objects.filter(id=to_table_id).update(
    #             no_of_attendant=old_no_of_attendent,
    #             customer=old_customer, status=old_status
    #         )
    #         # changing table key of order main
    #         OrderMain.objects.filter(id=main_id).\
    #             update(table=int(to_table_id))
    #         # updating 'from table' to vacant(1)
    #         Table.objects.filter(id=from_table.id)\
    #             .update(no_of_attendant=0, customer='', status=1)
    #         return Response("Table transferred", status=status.HTTP_200_OK)
    #     except ObjectDoesNotExist:
    #         return Response(
    #             "Order main or table with provied id not found",
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    # 




# Django-Rest_framework
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend, DateFromToRangeFilter
from rest_framework.filters import OrderingFilter, SearchFilter
import django_filters
from rest_framework.response import Response
# imported serializers
from .serializers import ItemCategorySerializer, ItemSubCategorySerializer
from .serializers import ItemSerializer

# imported models
from .models import ItemCategory, ItemSubCategory
from .models import Item
from .item_permissions import ItemPermission, ItemCategoryPermission
# for log
from simple_history.utils import update_change_reason


class FilterForItem(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Item
        fields = ['code', 'item_category__name',
                  'location', 'taxable', 'discountable']


class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemPermission]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_class = FilterForItem
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code']
    http_method_names = ['get', 'head', 'post', 'patch']

    def create(self, request, *args, **kwargs):
        print(request.FILES)
        print(request.data.items())
        # print(request.data.pop('image'))
        print(request.data)
        serialzier = ItemSerializer(data=request.data, context={'request': request})
        if serialzier.is_valid(raise_exception=True):
            serialzier.save()
            return Response(serialzier.data, status=status.HTTP_200_OK)
        else:
            return Response(serialzier.errors, status=status.HTTP_400_BAD_REQUEST)

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


class FilterForItemCategory(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = ItemCategory
        fields = ['display_order', 'active', 'code', 'date', 'name']


class ItemCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemCategoryPermission]
    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    filter_class = FilterForItemCategory
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code', 'display_order']
    http_method_names = ['get', 'head', 'post', 'patch']

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


class FilterForItemSubCategory(django_filters.FilterSet):
    date = DateFromToRangeFilter(field_name="created_date_ad")
    name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = ItemSubCategory
        fields = ['display_order', 'active', 'code', 'date', 'name']


class ItemSubCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [ItemCategoryPermission]
    queryset = ItemSubCategory.objects.all()
    serializer_class = ItemSubCategorySerializer
    filter_class = FilterForItemSubCategory
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ['name', 'code']
    ordering_fields = ['id', 'name', 'code', 'display_order']
    http_method_names = ['get', 'head', 'post', 'patch']

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

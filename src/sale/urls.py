from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import SaleMainView, SaleDetailView, SaveSaleView, ReturnSaleView, SaleDetailForReturnViewSet, \
    SalePaymentDetailView, SaleMainSaleView, SaleMainReturnView, SaleAdditionalChargeViewSet,\
        SalePrintLogViewset
router = DefaultRouter(trailing_slash=False)

# ViewSet registration from purchase
router.register("sale-master", SaleMainView)
router.register("sale-master-sale", SaleMainSaleView)
router.register("sale-master-return", SaleMainReturnView)
router.register("sale-detail", SaleDetailView)
router.register("get-sale-info", SaleDetailForReturnViewSet)
router.register("save-sale", SaveSaleView)
router.register("save-sale-return", ReturnSaleView)
router.register("sale-payment-detail", SalePaymentDetailView)
router.register("sale-additional-charge", SaleAdditionalChargeViewSet)
router.register("sale-print-log",SalePrintLogViewset)


urlpatterns = [
    path('', include(router.urls)),

]
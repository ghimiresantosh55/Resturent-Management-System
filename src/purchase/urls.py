from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PurchaseOrderDetailViewSet, \
    PurchaseMainViewSet, PurchaseDetailViewSet
from .views import SavePurchaseOrderView, CancelPurchaseOrderView, ApprovePurchaseOrderView, DirectApprovePurchaseView,\
    ReturnPurchaseView, GetUnAppUnCanPurchaseOrderMainView, PurchaseAdditionView, PurchaseMainReturnedViewSet,\
    PurchaseMainPurchaseViewSet, PurchaseOrderMainViewSet, PurchasePaymentDetailsViewSet, \
    PurchaseAdditionalChargeViewSet
from utils.views.stock_views import PurchaseDetailStockViewSet
router = DefaultRouter(trailing_slash=False)

# ViewSet registration from purchase
router.register("purchase-order-main", PurchaseOrderMainViewSet)
router.register("purchase-order-detail", PurchaseOrderDetailViewSet)
router .register('get-orders', GetUnAppUnCanPurchaseOrderMainView)
router.register("save-purchase-order", SavePurchaseOrderView)
router.register('cancel-purchase-order', CancelPurchaseOrderView)
router.register('approve-purchase-order', ApprovePurchaseOrderView)
router.register("purchase-main", PurchaseMainViewSet)
router.register("purchase-main-purchase", PurchaseMainPurchaseViewSet)
router.register("purchase-main-returned", PurchaseMainReturnedViewSet)
router.register("purchase-detail", PurchaseDetailViewSet)
router.register('direct-purchase', DirectApprovePurchaseView)
router.register('return-purchase', ReturnPurchaseView)
router.register('add-stock', PurchaseAdditionView)
router.register('get-stock-by-purchase', PurchaseDetailStockViewSet)
router.register('purchase-payment-detail', PurchasePaymentDetailsViewSet)
router.register('purchase-additional-charge', PurchaseAdditionalChargeViewSet)
urlpatterns = [
    path('', include(router.urls))
]

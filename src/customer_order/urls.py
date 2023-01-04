from rest_framework import routers

from django.urls import path, include

from .views import SaveOrderView, OrderMainViewSet, OrderDetailViewSet, OrderSummaryViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("save-order", SaveOrderView)

# Check where this URL is used???
router.register("order-main", OrderMainViewSet)
router.register("order-detail", OrderDetailViewSet)
router.register("order-summary", OrderSummaryViewSet)

urlpatterns = [
    path('', include(router.urls))
]

  
from rest_framework import routers

from django.urls import path, include

from .views import GetPartyInvoice,SavePartyClearanceViewSet, PartyClearanceViewSet,\
     PartyPaymentDetailViewSet, PartyClearanceSummaryViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("party-clearance", PartyClearanceViewSet)
router.register("party-clearance-payment-detail", PartyPaymentDetailViewSet)
router.register("party-clearance-summary", PartyClearanceSummaryViewSet)
router.register("get-party-invoice", GetPartyInvoice)
router.register("clear-party-invoice", SavePartyClearanceViewSet)


urlpatterns = [
    path('', include(router.urls))
]

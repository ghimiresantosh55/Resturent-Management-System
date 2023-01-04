from rest_framework import routers
from .views import BlockViewSet, TableViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("block", BlockViewSet)
router.register("table", TableViewSet)

urlpatterns = [

]+router.urls

from django.urls import path, include
from rest_framework import routers
from .views import ItemCategoryViewSet, ItemViewSet, ItemSubCategoryViewSet
router = routers.DefaultRouter(trailing_slash=False)
router.register("item", ItemViewSet)
router.register("item-category", ItemCategoryViewSet)
router.register("item-sub-category", ItemSubCategoryViewSet)
urlpatterns = [
    path('', include(router.urls))
]
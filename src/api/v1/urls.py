from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('doc', SpectacularRedocView.as_view(url_name='schema'), name='doc'),
    path('swagger', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('user-app/', include('src.user.urls')),
    path('user-group-app/', include('src.user_group.urls')),
    path('core-app/', include('src.core_app.urls')),
    path('customer-app/', include('src.customer.urls')),
    path('rims-setup-app/', include('src.rims_setup.urls')),
    path('item-app/', include('src.item.urls')),
    path('supplier-app/', include('src.supplier.urls')),
    path('customer-order-app/', include('src.customer_order.urls')),
    path('advance-deposit-app/', include('src.advance_deposit.urls')),
    path('credit-management-app/', include('src.credit_management.urls')),
    path('sale-app/', include('src.sale.urls'))
]

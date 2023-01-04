
from django.contrib import admin
import debug_toolbar
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tenant.views import TenantMapView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('src.api.urls')),
    path('branches', TenantMapView.as_view()),
    path('debug/', include(debug_toolbar.urls)),


              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

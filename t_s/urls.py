from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usr/', include('accounts.urls')),
    path('api/food/', include('foods.urls')),
    path('api/order/', include('orders.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

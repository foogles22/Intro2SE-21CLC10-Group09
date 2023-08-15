from django.contrib import admin
from django.urls import path,include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from . import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ad.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'ad.views.error_404_view'
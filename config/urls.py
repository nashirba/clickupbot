from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bot/', include('apps.bot.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

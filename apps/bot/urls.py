from django.urls import include, path
from .views import UserCodeRedirectView

urlpatterns = [
    path('access_code/', UserCodeRedirectView.as_view(), name='redirect_view'),
    path('webhook/', include('django_telegrambot.urls')),
]

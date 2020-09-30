from django.urls import include, path
from .views import UserCodeRedirectView #, EventView

urlpatterns = [
    path('access_code/', UserCodeRedirectView.as_view(), name='redirect_view'),
    path('webhook/', include('django_telegrambot.urls')),
    # path('event/' EventView.as_view, name='event_view')
]

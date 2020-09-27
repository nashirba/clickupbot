from django.urls import path
from .views import UserCodeRedirectView

urlpatterns = [
    path('', UserCodeRedirectView.as_view(), name='redirect_view'),
]

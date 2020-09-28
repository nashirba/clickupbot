from django.urls import include, path
# from django.views.decorators.csrf import csrf_exempt

from .views import UserCodeRedirectView

urlpatterns = [
    path('access_code/', UserCodeRedirectView.as_view(), name='redirect_view'),
    # path('webhook/', csrf_exempt(BotView.as_view())),
    path('webhook/', include('django_telegrambot.urls')),

]

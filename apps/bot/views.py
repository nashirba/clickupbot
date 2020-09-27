import requests

from django.conf import settings
from django.shortcuts import render
from django.views.generic.base import RedirectView

from .models import ClickupUser, TelegramUser


class UserCodeRedirectView(RedirectView):

    def get(self, request):
        try:
            print(request.GET)
            click_access_code = request.GET.get('code', None)

            # fix to get requested users
            tel_user = TelegramUser.objects.get(name='Нурлан')
            click_user = ClickupUser.objects.get(telegram_user=tel_user)
            click_user.reg_code = click_access_code

            client_id = settings.CLICKUP_CLIENT_ID
            client_secret = settings.CLICKUP_SECRET
            token_url = f'https://api.clickup.com/api/v2/oauth/token?client_id={client_id}&client_secret={client_secret}&code={click_access_code}'
            token_url_result = requests.post(token_url)
            clickup_token = token_url_result.json()['access_token']

            # fix to get requested users
            click_user.reg_token = clickup_token
            click_user.save()

            # get user
            auth_user_url = 'https://api.clickup.com/api/v2/user'
            headers = {'Authorization': click_user.reg_token}
            req = requests.get(auth_user_url, headers=headers)
            click_user.clickup_user_id = req.text['user']['id']
            click_user.username = req.text['user']['username']
            click_user.email = req.text['user']['email']
            click_user.save()
            print('clickup user object is update with id, email, username')
            
        except:
            pass

        return super().get(request)

    url = 'https://telegram.me/test_clickup_bot'

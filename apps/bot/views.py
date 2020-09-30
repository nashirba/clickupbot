import json
import requests

from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.generic.base import RedirectView

from .models import ClickupUser, Message, TelegramUser

TELEGRAM_URL = 'https://api.telegram.org/bot'


def send_message(message, chat_id):
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        response = requests.post(f"{TELEGRAM_URL}{settings.BOT_TOKEN}/sendMessage", data=data)


class UserCodeRedirectView(RedirectView):    

    def get(self, request):
        try:
            # fix click_user var to get requested users
            last_login_mes = Message.objects.filter(text='logingetloginget').last()
            tel_user = last_login_mes.telegram_user
            click_user = ClickupUser.objects.get(telegram_user=tel_user)

            # get token
            click_access_code = request.GET.get('code', None)
            click_user.reg_code = click_access_code
            client_id = settings.CLICKUP_CLIENT_ID
            client_secret = settings.CLICKUP_SECRET
            token_url = f'https://api.clickup.com/api/v2/oauth/token?client_id={client_id}&client_secret={client_secret}&code={click_access_code}'
            token_url_result = requests.post(token_url)
            clickup_token = token_url_result.json()['access_token']
            click_user.reg_token = clickup_token
            click_user.save()

            # lets notify user of susseccful get token action
            text = 'Your 🔑token has been successfully saved ✅ \nPlease type /start again'
            send_message(text, tel_user.chat_id)

            # get user
            auth_user_url = 'https://api.clickup.com/api/v2/user'
            headers = {'Authorization': clickup_token}
            req = requests.get(auth_user_url, headers=headers)
            click_user.clickup_user_id = req.json()['user']['id']
            click_user.username = req.json()['user']['username']
            click_user.email = req.json()['user']['email']
            click_user.save()
            logger.info("clickup user object is updated with id, email, username")

        except:
            pass

        return super().get(request)

    url = 'https://telegram.me/test_clickup_bot'


# class EventView(View):

#     def post(self, request, *args, **kwargs):
#         t_data = json.loads(request.body)
#         t_message = t_data["message"]
#         t_chat = t_message["chat"]

#         try:
#             text = t_message["text"].strip().lower()
#         except Exception as e:
#             return JsonResponse({"ok": "POST request processed"})

#         text = text.lstrip("/")
#         chat = tb_tutorial_collection.find_one({"chat_id": t_chat["id"]})
#         msg = "Unknown command"
#         send_message(msg, t_chat["id"])

#         return JsonResponse({"ok": "POST request processed"})

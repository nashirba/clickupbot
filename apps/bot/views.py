# import logging
# import re
import requests
# import telegram

from django.conf import settings
# from django.shortcuts import render
# from django.views import View
from django.views.generic.base import RedirectView

# from telegram import LoginUrl, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, MessageHandler, 
#                         InlineQueryHandler, Filters)

from .models import ClickupUser, Message, TelegramUser

# webhook_url = 'https://api.telegram.org/bot1088802586:AAEfgAPyQbOTaJNCOqc2ZehSaX6FeAx_aX8/setWebhook?url=https://a1af39e33003.ngrok.io/bot/webhook/'


# def start(update, context):
#     name = update.message.chat.first_name
#     chat_id = update.effective_chat.id
#     tel_user, tel_created = TelegramUser.objects.get_or_create(chat_id=chat_id, name=name)
#     if tel_created:
#         print('new telegram user')
#         text = '{}, welcome to ClickUp bot.'.format(name)
#         ClickupUser.objects.create(telegram_user=tel_user)
#         print('clickup user instance created')
#     else:
#         text = '{}, welcome back again.'.format(name)
#     context.bot.send_message(chat_id=chat_id, text=text)
    
#     click_user = ClickupUser.objects.get(telegram_user=tel_user)
#     if click_user.reg_token:
#         return command_list(update, context)
#     return login(update, context)
    

# def do_echo(update, context):
#     chat_id = update.message.chat.id
#     text = update.message.text
#     name = update.message.chat.first_name
#     tel_user, _ = TelegramUser.objects.get_or_create(chat_id=chat_id, defaults={'name':name})
#     mes = Message(telegram_user=tel_user, text=text)
#     mes.save()
#     reply_text = f'{name}, please type /start to initiate'
#     update.message.reply_text(text=reply_text)


# def command_list(update, context):
#     update.message.reply_text('Task search started. Please wait it will take a while to process')
#     chat_id = update.effective_chat.id
#     tel_user = TelegramUser.objects.get(chat_id=chat_id)
#     click_user = ClickupUser.objects.get(telegram_user=tel_user)
#     team_url = 'https://api.clickup.com/api/v2/team'
#     headers = {'Authorization': click_user.reg_token}
#     req = requests.get(team_url, headers=headers)
#     print('task search started')
#     teams_id_list = []
#     for item in req.json()['teams']:
#         teams_id_list.append(item['id'])
#     space_id_list = []
#     for team_id_item in teams_id_list:
#         space_url = f'https://api.clickup.com/api/v2/team/{team_id_item}/space?archived=false'
#         req = requests.get(space_url, headers=headers)
#         for i in req.json()['spaces']:
#             space_id_list.append(i['id'])
#     folder_id_list = []
#     for space_id_item in space_id_list:
#         folder_url = f'https://api.clickup.com/api/v2/space/{space_id_item}/folder?archived=false'
#         req = requests.get(folder_url, headers=headers)
#         for i in req.json()['folders']:
#             folder_id_list.append(i['id'])
#     clickup_lists_items = []
#     for folder_id_item in folder_id_list:
#         list_url = f'https://api.clickup.com/api/v2/folder/{folder_id_item}/list?archived=false'
#         req = requests.get(list_url, headers=headers)
#         for i in req.json()['lists']:
#             clickup_lists_items.append(i['id'])
#     result_task = []
#     for clickup_lists_item in clickup_lists_items:
#         task_url = f'https://api.clickup.com/api/v2/list/{clickup_lists_item}/task?archived=false'
#         req = requests.get(task_url, headers=headers)
#         for task_item in req.json()['tasks']:
#             if task_item['assignees']:
#                 for task_assignee in task_item['assignees']:
#                     if click_user.username in task_assignee['username']:
#                         result_task_dict = {}
#                         result_task_dict['name'] = task_item['name']
#                         result_task_dict['text_content'] = task_item['text_content']
#                         result_task_dict['description'] = task_item['description']
#                         result_task_dict['status'] = task_item['status']['status']
#                         # result_task_dict['date_created'] = task_item['date_created']
#                         result_task_dict['creator'] = task_item['creator']['username']
#                         result_task.append(result_task_dict)
#     for result_task_item in result_task:
#         update.message.reply_text(result_task_item)


# def help(update, context):
#     update.message.reply_text("Use /start to test this bot.")


# def login(update, context):
#     chat_id = update.message.chat.id
#     client_id = settings.CLICKUP_CLIENT_ID
#     redirect_uri = settings.REDIRECT_URI
#     url = f'https://app.clickup.com/api?client_id={client_id}&redirect_uri={redirect_uri}?chat_id={chat_id}'
#     login_url = LoginUrl(url=url, bot_username='test_clickup_bot')
#     reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Get Token',login_url=login_url)]])
#     update.message.reply_text('Please press button:', reply_markup=reply_markup)


# class BotView(View):
#     '''
#     All messages will be redirected here from telegram server. 
#     Used setWebhook method see telegram api docs
#     '''

#     def post(self, request, *args, **kwargs):
#         """Start the bot if post method received from telegram server."""
#         print('*************************')
#         print(request)
#         print('*************************')
#         updater = Updater(settings.BOT_TOKEN, use_context=True)

#         # Get the dispatcher to register handlers
#         dp = updater.dispatcher

#         # Get the dispatcher to register handlers
#         dp.add_handler(CommandHandler("start", start))
#         dp.add_handler(CommandHandler("help", help))
#         # dp.add_handler(CommandHandler("test", test))
#         dp.add_handler(CommandHandler("login", login))

#         message_handler = MessageHandler(Filters.text, do_echo)
#         dp.add_handler(message_handler)

#         # Start the Bot
#         updater.start_polling()

#         # # Run the bot until you press Ctrl-C or the process receives SIGINT,
#         # # SIGTERM or SIGABRT. This should be used most of the time, since
#         # # start_polling() is non-blocking and will stop the bot gracefull
#         # updater.idle()


class UserCodeRedirectView(RedirectView):

    def get(self, request):
        try:
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


# import json
# import os

# import requests
# from django.http import JsonResponse


# TELEGRAM_URL = "https://api.telegram.org/bot"

# class BotView(View):

#     def post(self, request, *args, **kwargs):
#         t_data = json.loads(request.body)
#         t_message = t_data["message"]
#         t_chat = t_message["chat"]
#         try:
#             text = t_message["text"].strip().lower()
#         except Exception as e:
#             return JsonResponse({"ok": "POST request processed"})

#         # text = text.lstrip("/")
#         print(text)
#         # if string lest try invoke echo command
#         try:
#             if text.find('start'):
#                 print('hi there')

#         except:
#             print('--------------------N O T--W O R K I N G----------------')
        
#         msg = "Unknown command"
#         self.send_message(msg, t_chat["id"])

#         return JsonResponse({"ok": "POST request processed"})

#     @staticmethod
#     def send_message(message, chat_id):
#         data = {
#             "chat_id": chat_id,
#             "text": message,
#             "parse_mode": "Markdown",
#         }
#         response = requests.post(
#             f"{TELEGRAM_URL}{settings.BOT_TOKEN}/sendMessage", data=data
#         )
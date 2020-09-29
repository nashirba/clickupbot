import logging
import requests

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from django.conf import settings
from django_telegrambot.apps import DjangoTelegramBot

from .models import ClickupUser, Message, TelegramUser


logger = logging.getLogger(__name__)


def start(bot, update):
    if update.callback_query:
        name = update.callback_query.message.chat.first_name
    else:
        name = update.message.chat.first_name
    chat_id = update.effective_chat.id
    tel_user, tel_created = TelegramUser.objects.get_or_create(chat_id=chat_id, name=name)
    click_user, click_user_created = ClickupUser.objects.get_or_create(telegram_user=tel_user)
    if tel_created or click_user_created:
        text = '{}, welcome to ClickUp bot 🎉'.format(name)
        bot.sendMessage(chat_id, text=text)
        return login(bot, update)
    elif click_user.reg_token:
        text = '{}, welcome back again 💫'.format(name)
        bot.sendMessage(chat_id, text=text)
        return commands(bot, update)
    else:
        text = '{}, your 🔑token is not set up ⛔️'.format(name)
        bot.sendMessage(chat_id, text=text)
        return login(bot, update)


def commands(bot, update):
    if update.callback_query:
        name = update.callback_query.message.chat.first_name
    else:
        name = update.message.chat.first_name
    chat_id = update.effective_chat.id
    try:
        # check if users are created already
        tel_user = TelegramUser.objects.get(chat_id=chat_id, name=name)
        click_user = ClickupUser.objects.get(telegram_user=tel_user)
        # lets return avaiable commands
        keyboard = [[InlineKeyboardButton("Get Task", callback_data='task')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # update.message.reply_text('Please choose commands ⤵️:', reply_markup=reply_markup)
        text = 'Please choose commands ⤵️:'
        bot.sendMessage(chat_id, text=text, reply_markup=reply_markup)
    except:
        text = '''🙅‍♂️ you need set your account first⛔️'''
        bot.sendMessage(chat_id, text=text)
        return start(bot, update)


def button(bot, update):
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    if query.data == 'task':
        get_task(bot, update)
    if query.data == 'start':
        start(bot, update)


def get_task(bot, update):
    try:
        chat_id = update.effective_chat.id
        tel_user = TelegramUser.objects.get(chat_id=chat_id)
        click_user = ClickupUser.objects.get(telegram_user=tel_user)
    except:
        text = 'You didnt set your account yet.'
        bot.sendMessage(chat_id, text=text)
        return start(bot, update)
    if not click_user.reg_token:
        text = '{}, your 🔑token is not set up ⛔️'.format(tel_user.name)
        bot.sendMessage(chat_id, text=text)
        return login(bot, update)
    text = 'Task search started 🔎. Please wait, it will take a while to process...'
    bot.sendMessage(chat_id, text=text)
    team_url = 'https://api.clickup.com/api/v2/team'
    headers = {'Authorization': click_user.reg_token}
    req = requests.get(team_url, headers=headers)
    teams_id_list = []
    for item in req.json()['teams']:
        teams_id_list.append(item['id'])
    space_id_list = []
    for team_id_item in teams_id_list:
        space_url = f'https://api.clickup.com/api/v2/team/{team_id_item}/space?archived=false'
        req = requests.get(space_url, headers=headers)
        for i in req.json()['spaces']:
            space_id_list.append(i['id'])
    folder_id_list = []
    for space_id_item in space_id_list:
        folder_url = f'https://api.clickup.com/api/v2/space/{space_id_item}/folder?archived=false'
        req = requests.get(folder_url, headers=headers)
        for i in req.json()['folders']:
            folder_id_list.append(i['id'])
    clickup_lists_items = []
    for folder_id_item in folder_id_list:
        list_url = f'https://api.clickup.com/api/v2/folder/{folder_id_item}/list?archived=false'
        req = requests.get(list_url, headers=headers)
        for i in req.json()['lists']:
            clickup_lists_items.append(i['id'])
    text = "I'm still looking 👀"
    bot.sendMessage(chat_id, text=text)
    result_task = []
    for clickup_lists_item in clickup_lists_items:
        task_url = f'https://api.clickup.com/api/v2/list/{clickup_lists_item}/task?archived=false'
        req = requests.get(task_url, headers=headers)
        for task_item in req.json()['tasks']:
            if task_item['assignees']:
                for task_assignee in task_item['assignees']:
                    if click_user.username in task_assignee['username']:
                        result_task_dict = {}
                        result_task_dict['name'] = task_item['name']
                        result_task_dict['text_content'] = task_item['text_content']
                        result_task_dict['description'] = task_item['description']
                        result_task_dict['status'] = task_item['status']['status']
                        # result_task_dict['date_created'] = task_item['date_created']
                        result_task_dict['creator'] = task_item['creator']['username']
                        result_task.append(result_task_dict)
    if result_task:
        text = f'Done, you have {len(result_task)} 📝message(s)'
        bot.sendMessage(chat_id, text=text)
        for task_number, result_task_item in enumerate(result_task, 1):
            text = f'''📌 task #{task_number}
🔘 name: {result_task_item['name']}.
▫️ content: {result_task_item['text_content']}.
▫️ description: {result_task_item['description']}.
▫️ status: {result_task_item['status']}.
▫️ created by {result_task_item['creator']}.
'''
            bot.sendMessage(chat_id, text=text)
    else:
        text = "You don't have any task, lucky you 🤩"
        bot.sendMessage(chat_id, text=text)


def help(bot, update):
    name = update.message.chat.first_name
    chat_id = update.effective_chat.id
    text = '''{}, this bot is integrated into ClickUp application.
type /start to initiate
type /commands to see all commands'''.format(name)
    bot.sendMessage(chat_id, text=text)


def do_echo(bot, update):
    chat_id = update.effective_chat.id
    text = update.message.text
    name = update.message.chat.first_name
    tel_user, _ = TelegramUser.objects.get_or_create(chat_id=chat_id, defaults={'name':name})
    mes = Message(telegram_user=tel_user, text=text)
    mes.save()

    # lets return avaiable commands
    keyboard = [[InlineKeyboardButton("Start", callback_data='start')],
                [InlineKeyboardButton("Get Task", callback_data='task')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose commands ⤵️:', reply_markup=reply_markup)


def login(bot, update):
    chat_id = update.effective_chat.id
    client_id = settings.CLICKUP_CLIENT_ID
    redirect_uri = settings.REDIRECT_URI
    url = f'https://app.clickup.com/api?client_id={client_id}&redirect_uri={redirect_uri}?chat_id={chat_id}'
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Get Token',url=url)]])
    reply_text = 'Please press button ⤵️:'
    bot.sendMessage(chat_id, text=reply_text, reply_markup=reply_markup)
    
    # let's add message to db so that UserCodeRedirectView will check it to get user data
    text = 'loginget'
    name = update.message.chat.first_name
    tel_user = TelegramUser.objects.get(chat_id=chat_id, name=name)
    mes = Message(telegram_user=tel_user, text=text)
    mes.save()


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    logger.info("Loading handlers for telegram bot")

    # Default dispatcher (this is related to the first bot in settings.DJANGO_TELEGRAMBOT['BOTS'])
    dp = DjangoTelegramBot.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("commands", commands))
    dp.add_handler(CommandHandler("task", get_task))
    dp.add_handler(CallbackQueryHandler(button))


    message_handler = MessageHandler(Filters.text, do_echo)
    dp.add_handler(message_handler)


    # log all errors
    dp.add_error_handler(error)

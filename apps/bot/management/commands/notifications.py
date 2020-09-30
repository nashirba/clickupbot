import datetime
import requests
import schedule
import time

from django.conf import settings
from apps.bot.models import ClickupUser

TELEGRAM_URL = 'https://api.telegram.org/bot'


def send_message(message, chat_id):
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        response = requests.post(f"{TELEGRAM_URL}{settings.BOT_TOKEN}/sendMessage", data=data)


def daily_task_updater():
    click_users = ClickupUser.objects.all()
    for click_user in click_users:
        if click_user.reg_token and click_user.reminder == True:
            tel_user = click_user.telegram_user
            chat_id = tel_user.chat_id
            name = tel_user.name
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
                                date_created_int = int(task_item['date_created'])
                                date = datetime.datetime.fromtimestamp(date_created_int/1e3)
                                result_task_dict['date_created'] = date
                                result_task_dict['creator'] = task_item['creator']['username']
                                result_task.append(result_task_dict)
            if result_task:
                text = f'Good morning {name} 👋, \nyou have {len(result_task)} clickup 📝task(s) \nhave a nice & productive day 💪'
                send_message(text, chat_id)
                for task_number, result_task_item in enumerate(result_task, 1):
                    text = f'''📌 task #{task_number}
🔘 name: {result_task_item['name']}
▫️ content: {result_task_item['text_content']}
▫️ description: {result_task_item['description']}
▫️ status: {result_task_item['status']}
▫️ created by {result_task_item['creator']}
▫️ date: {result_task_dict['date_created'].day}.{result_task_dict['date_created'].month}.{result_task_dict['date_created'].year}
'''
                send_message(text, chat_id)

# for testing
schedule.every(1).minutes.do(daily_task_updater)
# for production. note => -6 hours time difference 
schedule.every().monday.at("03:00").do(daily_task_updater)
schedule.every().tuesday.at("03:00").do(daily_task_updater)
schedule.every().wednesday.at("03:00").do(daily_task_updater)
schedule.every().thursday.at("03:00").do(daily_task_updater)
schedule.every().friday.at("03:00").do(daily_task_updater)


while True:
    schedule.run_pending()
    time.sleep(1)

from django.contrib import admin
from .models import ClickupUser, Message, TelegramUser

admin.site.register(ClickupUser)
admin.site.register(Message)
admin.site.register(TelegramUser)

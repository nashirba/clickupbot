from django.contrib import admin
from .models import ClickupUser, Message, TelegramUser


admin.site.register(ClickupUser)
admin.site.register(Message)
admin.site.register(TelegramUser)

'''
@admin.register(ClickupUser)
class ClickupUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('name')
'''
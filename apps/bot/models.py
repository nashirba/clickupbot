from django.contrib.auth import get_user_model
from django.db import models


class TelegramUser(models.Model):
    chat_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'Telegram user {self.name}'

    class Meta:
        verbose_name = 'Telegram Profile'
        verbose_name_plural = 'Telegram Profiles'


class ClickupUser(models.Model):
    telegram_user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE)
    clickup_user_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    reg_code = models.CharField(max_length=48, null=True, blank=True)
    reg_token = models.CharField(max_length=48, null=True, blank=True)

    def __str__(self):
        return f'Clickup user {self.username}'

    class Meta:
        verbose_name = 'Clickup Profile'
        verbose_name_plural = 'Clickup Profiles'


#delete later, only for testing
class Message(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message #{self.pk} from {self.telegram_user} on {self.created_date}'

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
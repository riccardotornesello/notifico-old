from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
    path(f'telegram/{settings.TELEGRAM_WEBHOOK_TOKEN}',
         views.TelegramList.as_view(), name='telegram'),
]

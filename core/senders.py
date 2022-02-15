import requests
from django.conf import settings


class LOG_LEVEL(dict):
    ERROR = 'error'
    WARNING = 'warning'
    SUCCESS = 'success'
    INFO = 'info'


ICONS = {
    LOG_LEVEL.ERROR: '❌',
    LOG_LEVEL.WARNING: '⚠️',
    LOG_LEVEL.SUCCESS: '✅',
    LOG_LEVEL.INFO: '💬'
}


def gen_message(message, log_level, header):
    icon = ICONS[log_level] if log_level else ''
    first_line_strings = [icon, header, icon]
    first_line = ' '.join(filter(None, first_line_strings))
    return '\n'.join(filter(None, [first_line, message]))


def telegram_send(chat_id, message):
    return requests.post(f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                         data={'chat_id': chat_id, 'text': message, 'parse_mode': 'markdownv2'})


def _telegram(options, message):
    return requests.post(f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                         data={'chat_id': options['chat_id'], 'text': message, 'parse_mode': 'markdownv2'})


def _discord(options, message):
    return requests.post(options['webhook_url'], data={'content': message})

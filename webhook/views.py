import json
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from core.models import *
from core.redis import redis_client
from core.senders import LOG_LEVEL, gen_message, telegram_send


class TelegramList(APIView):
    def post(self, request, format=None):
        telegram_request = json.loads(request.body)

        # Check if it is a message event
        if not 'message' in telegram_request:
            return HttpResponse('')

        message = telegram_request['message']

        message_text = message['text'].split(' ')
        message_chat = message['chat']['id']

        # Handle "enable" command
        if message_text[0] == '/enable' and len(message_text) == 2:
            # Code in format project_id:key
            enable_code = message_text[1].split(':')
            if not len(enable_code) == 2:
                message = gen_message(None, LOG_LEVEL.ERROR, 'Invalid code')
                telegram_send(message_chat, message)
                return HttpResponse('')

            project_id = enable_code[0]
            key = enable_code[1]
            redis_result = redis_client.getdel(f'connect:{project_id}')
            print(redis_result)
            # If not found on redis
            if not redis_result:
                message = gen_message(None, LOG_LEVEL.ERROR, 'Invalid code')
                telegram_send(message_chat, message)
                return HttpResponse('')

            value = json.loads(redis_result)
            # Check if key is correct
            if key != value['key']:
                message = gen_message(None, LOG_LEVEL.ERROR, 'Invalid code')
                telegram_send(message_chat, message)
                return HttpResponse('')

            # Check channels limit
            channels_count = Channel.objects.filter(
                project__id=project_id).count()
            if channels_count >= settings.CHANNELS_LIMIT:
                message = gen_message(
                    None, LOG_LEVEL.ERROR, 'Channels limit reached')
                telegram_send(message_chat, message)
                return HttpResponse('')

            project = Project.objects.filter(id=project_id).first()
            options = {
                'chat_id': message_chat
            }

            duplicates = Channel.objects.filter(
                type='telegram', options=options, project=project).count()
            if duplicates > 0:
                message = gen_message(
                    None, LOG_LEVEL.ERROR, f'The project `{project.name}` has already been added to this chat')
                telegram_send(message_chat, message)
                return HttpResponse('')

            channel = Channel(
                name=value['channel_name'], type='telegram', options=options, project=project)
            channel.save()
            message = gen_message(
                None, LOG_LEVEL.SUCCESS, f'Channel registered in project `{project.name}` as `{channel.name}`')
            channel.send(message)

        else:
            message = gen_message(None, LOG_LEVEL.WARNING, 'Invalid command')
            telegram_send(message_chat, message)

        return HttpResponse('')

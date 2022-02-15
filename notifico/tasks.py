import subprocess
from celery import shared_task


@shared_task
def checker(frequency):
    from core.models import Channel, Test
    from core.senders import LOG_LEVEL, gen_message

    tests = Test.objects.filter(frequency=frequency)
    for test in tests:
        old_working = test.working
        test.run()
        if old_working != test.working:
            if test.working == True:
                message = gen_message(
                    None, LOG_LEVEL.SUCCESS, f'Host `{test.name}` has become up in project `{test.project.name}`')
            else:
                message = gen_message(
                    None, LOG_LEVEL.ERROR, f'Host {test.name} has become down in project `{test.project.name}`')

            channels = Channel.objects.filter(project__id=test.project.id)
            for channel in channels:
                channel.send(message)

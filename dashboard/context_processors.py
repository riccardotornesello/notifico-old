from django.conf import settings


def settings_constants(request):
    return {
        'GTAG': settings.GTAG,
        'PROJECTS_LIMIT': settings.PROJECTS_LIMIT,
        'TESTS_LIMIT': settings.TESTS_LIMIT,
        'CHANNELS_LIMIT': settings.CHANNELS_LIMIT,
    }

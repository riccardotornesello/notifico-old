from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from . import senders, tests


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Project(models.Model):
    name = models.CharField(max_length=30)
    api_key = models.CharField(max_length=32, unique=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )


class Channel(models.Model):
    name = models.CharField(max_length=32)
    type = models.CharField(max_length=30)
    options = models.JSONField()

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def send(self, message):
        send_functions = {
            'discord': senders._discord,
            'telegram': senders._telegram
        }
        return send_functions[self.type](self.options, message)


class Test(models.Model):
    name = models.CharField(max_length=32)
    type = models.CharField(max_length=10)
    frequency = models.CharField(max_length=5)
    options = models.JSONField()
    working = models.BooleanField()

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def run(self):
        test_functions = {
            'ping': tests.ping
        }
        working = test_functions[self.type](self.options)
        self.working = working
        self.save()

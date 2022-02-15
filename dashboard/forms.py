import uuid
from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import *

# TODO: login with email
class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

# TODO: clean like forms in Project page
class ProjectCreateForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Name here",
                "class": "form-control"
            }
        ),
        max_length=30)

    class Meta:
        model = Project
        fields = ('name')

    def save(self, user, commit=True):
        project = Project(
            name=self.cleaned_data['name'], api_key=uuid.uuid4().hex, owner=user)
        if commit:
            project.save()
        return project


class BaseChannelCreateForm(forms.Form):
    name = forms.CharField(
        max_length=32,
        required=True,
        label='Channel name',
        widget=forms.TextInput(
            attrs={
                "placeholder": "Name here",
                "class": "form-control"
            }
        )
    )


class TelegramChannelCreateForm(BaseChannelCreateForm):
    pass


class DiscordChannelCreateForm(BaseChannelCreateForm):
    url = forms.URLField(
        required=True,
        label='Discord webhook url',
        initial='https://discord.com/api/webhooks/',
        widget=forms.TextInput(
            attrs={
                "placeholder": "Url here",
                "class": "form-control"
            }
        )
    )


class BaseTestCreateForm(forms.Form):
    FREQUENCY_CHOICES = [
        ('1m', 'Every minute'),
        ('5m', 'Every 5 minutes'),
        ('1h', 'Every hour'),
    ]

    name = forms.CharField(
        max_length=32,
        required=True,
        label='Test name',
        widget=forms.TextInput(
            attrs={
                "placeholder": "Name here",
                "class": "form-control"
            }
        )
    )

    frequency = forms.ChoiceField(
        required=True,
        choices=FREQUENCY_CHOICES,
        label='Test frequency',
        widget=forms.Select(
            choices=FREQUENCY_CHOICES,
            attrs={
                "placeholder": "Name here",
                "class": "form-control"
            })
    )

# TODO: exclude dangrous IPs
class PingTestCreateForm(BaseTestCreateForm):
    host = forms.GenericIPAddressField(
        required=True,
        protocol='ipv4',
        label='Host IP',
        widget=forms.TextInput(
            attrs={
                "placeholder": "IP here",
                "class": "form-control"
            }
        )
    )

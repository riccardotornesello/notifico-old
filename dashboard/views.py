import json
from random import randint
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from core.models import *
from core.redis import redis_client
from core.senders import LOG_LEVEL, gen_message
from .forms import *
from .tokens import default_token_generator


class RegisterView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request=request, template_name='home/register.html', context={'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your Notifico account'
            message = render_to_string('email/confirm.html', {
                'user': user,
                'domain': current_site.domain,
                'token': default_token_generator.make_token(user)[0],
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            messages.success(
                request, 'Please confirm your email address to complete the registration')
            return redirect('login')
        return render(request=request, template_name='home/register.html', context={'form': form})


class ConfirmEmailView(View):
    def get(self, request, token):
        valid, user = default_token_generator.check_token(token)
        if valid:
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, 'Account confirmed!')
            return redirect('dashboard')
        else:
            return HttpResponse('Activation link is invalid!')


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request=request, template_name='home/login.html', context={'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET.get('next', 'dashboard'))
            else:
                messages.error(request, 'Invalid username or password.')
        return render(request=request, template_name='home/login.html', context={'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')


class IndexView(View):
    def get(self, request):
        return render(request=request, template_name='home/index.html')


class DashboardView(View):
    def get(self, request):
        projects = Project.objects.filter(owner=request.user)
        form = ProjectCreateForm()
        projects_left = settings.PROJECTS_LIMIT - len(projects)
        return render(request=request, template_name='home/dashboard.html', context={'project_form': form, 'projects': projects, 'projects_left': projects_left, 'segment': 'dashboard'})

    def post(self, request):
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            projects_count = Project.objects.filter(owner=request.user).count()
            if projects_count >= settings.PROJECTS_LIMIT:
                return HttpResponse('projects limit reached')

            project = form.save(request.user)
            return redirect('project', project_id=project.id)
        else:
            projects = Project.objects.filter(owner=request.user)
            return render(request=request, template_name='home/dashboard.html', context={'project_form': form, 'projects': projects, 'segment': 'dashboard'})


class ProjectView(TemplateView):
    http_method_names = ['get', 'post', 'delete']
    template_name = 'home/project.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['segment'] = 'dashboard'
        context['project'] = self.project
        context['channels'] = self.channels
        context['tests'] = self.tests
        context['channels_left'] = self.channels_left
        context['tests_left'] = self.tests_left
        context['ping_form'] = self.ping_form
        context['discord_form'] = self.discord_form
        context['telegram_form'] = self.telegram_form
        context['open_modal'] = self.open_modal
        return context

    def update_project_info(self):
        self.channels = Channel.objects.filter(project=self.project)
        self.tests = Test.objects.filter(project=self.project)
        self.channels_left = settings.CHANNELS_LIMIT - len(self.channels)
        self.tests_left = settings.TESTS_LIMIT - len(self.tests)

    def dispatch(self, *args, **kwargs):
        # Check if project exists
        self.project = Project.objects.filter(
            id=kwargs['project_id'], owner=self.request.user).first()
        if not self.project:
            raise Http404()

        # Save useful information in instance
        self.update_project_info()
        self.open_modal = None  # Open modal if errors
        self.ping_form = PingTestCreateForm()
        self.discord_form = DiscordChannelCreateForm()
        self.telegram_form = TelegramChannelCreateForm()

        # Allow methos like PUT and DELETE from forms
        method = self.request.POST.get('_method', '').lower()
        if method == 'put':
            return self.put(*args, **kwargs)
        if method == 'delete':
            return self.delete(*args, **kwargs)
        return super(ProjectView, self).dispatch(*args, **kwargs)

    def post(self, request, project_id):
        # Get the reason of the request
        request_type = request.POST.get('type', '')

        if request_type == 'telegram' and self.channels_left > 0:
            self.telegram_form = TelegramChannelCreateForm(self.request.POST)
            if self.telegram_form.is_valid():
                key = str(randint(100000, 999999))
                value = {
                    'key': key,
                    'channel_name': self.telegram_form.cleaned_data.get('name')
                }
                redis_client.set(
                    f'connect:{project_id}', json.dumps(value), ex=300)
                messages.success(
                    request, f'Use the command /enable {str(project_id)}:{key} in the bot channel')

                self.update_project_info()
            else:
                self.open_modal = 'telegram'

        elif request_type == 'discord' and self.channels_left > 0:
            self.discord_form = DiscordChannelCreateForm(self.request.POST)
            if self.discord_form.is_valid():
                name = self.discord_form.cleaned_data.get('name')
                options = {
                    'webhook_url': self.discord_form.cleaned_data.get('url')
                }

                duplicates = Channel.objects.filter(
                    type='discord', options=options, project=self.project).count()
                if duplicates > 0:
                    messages.error(
                        request, 'The same webhook has already been registered.')
                else:
                    channel = Channel(name=name, type='discord',
                                      options=options, project=self.project)
                    channel.save()

                    message = gen_message(
                        None, LOG_LEVEL.SUCCESS, f'Channel registered in project `{self.project.name}`')
                    channel.send(message)

                    self.update_project_info()
            else:
                self.open_modal = 'discord'

        elif request_type == 'ping' and self.tests_left > 0:
            self.ping_form = PingTestCreateForm(self.request.POST)
            if self.ping_form.is_valid():
                name = self.ping_form.cleaned_data.get('name')
                frequency = self.ping_form.cleaned_data.get('frequency')
                options = {
                    'host': self.ping_form.cleaned_data.get('host')
                }

                duplicates = Test.objects.filter(
                    type='ping', options=options, project=self.project).count()
                if duplicates > 0:
                    messages.error(
                        request, 'The same IP has already been added for this test.')
                else:
                    test = Test(name=name, type='ping', frequency=frequency,
                                options=options, working=True, project=self.project)
                    test.save()

                    self.update_project_info()
            else:
                self.open_modal = 'ping'

        return super(ProjectView, self).get(request, project_id)

    def delete(self, request, project_id):
        object_type = request.POST.get('type', '')
        object_id = request.POST.get('id', '')

        if object_type == 'channel':
            Channel.objects.filter(id=object_id, project=self.project).delete()
        elif object_type == 'test':
            Test.objects.filter(id=object_id, project=self.project).delete()

        self.update_project_info()
        return super(ProjectView, self).get(request, project_id)

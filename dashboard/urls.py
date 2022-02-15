import uuid
from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import ConfirmEmailView, DashboardView, IndexView, LoginView, LogoutView, ProjectView, RegisterView

from . import views

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('register', RegisterView.as_view(), name='register'),
    path('confirm/<str:token>', ConfirmEmailView.as_view(), name='confirm'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('dashboard', login_required(DashboardView.as_view()), name='dashboard'),
    path('dashboard/projects/<int:project_id>', login_required(ProjectView.as_view()), name='project'),
]

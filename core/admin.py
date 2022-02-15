from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import *

admin.site.register(User, UserAdmin)
admin.site.register(Channel)
admin.site.register(Project)
admin.site.register(Test)

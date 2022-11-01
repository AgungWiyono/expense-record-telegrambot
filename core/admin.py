from django.contrib import admin
from django.contrib.auth.models import Group

from core import models

admin.site.unregister(Group)
admin.site.register(models.User)

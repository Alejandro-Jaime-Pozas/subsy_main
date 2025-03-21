from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Company)
admin.site.register(models.LinkedBank)
admin.site.register(models.BankAccount)
admin.site.register(models.Transaction)
admin.site.register(models.Application)
admin.site.register(models.Subscription)
admin.site.register(models.Tag)

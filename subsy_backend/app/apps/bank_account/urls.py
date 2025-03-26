"""URL mappings for the bank_account app."""


from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views

app_name = 'apps.bank_account'

router = DefaultRouter()

router.register('bank-accounts', views.BankAccountViewSet, basename='bank-account')  # prefix is plural companies since appears in actual url, basename is singular company since it's the model name used for internal django reference

urlpatterns = [
    path('', include(router.urls))
]

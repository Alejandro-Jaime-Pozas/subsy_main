from django.urls import path
from . import views

urlpatterns = [
    path('create_link_token/', views.create_link_token, name='create_link_token'),
    path('exchange_public_token/', views.exchange_public_token, name='exchange_public_token'),
    path('balance/', views.get_balance, name='get_balance'),
    path('csrf_token/', views.csrf_token, name='csrf_token'),
    path('get_transactions/', views.get_transactions, name='get_transactions'),
]

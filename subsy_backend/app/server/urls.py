from django.urls import path
from . import views

urlpatterns = [
    path('create_link_token/', views.create_link_token, name='create_link_token'),
    path('exchange_public_token/', views.exchange_public_token, name='exchange_public_token'),
    path('balance/', views.get_balance, name='get_balance'),
    path('csrf_token/', views.csrf_token, name='csrf_token'),
    path('get_latest_transactions/', views.get_latest_transactions, name='get_latest_transactions'),
    path('get_all_transactions/', views.get_all_transactions, name='get_all_transactions'),
]

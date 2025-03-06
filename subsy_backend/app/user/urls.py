"""
URL mappings for the User api.
"""
from django.urls import path

from user import views


app_name = 'user'  # for reverse fn

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create')
]

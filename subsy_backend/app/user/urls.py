"""
URL mappings for the User api.
"""
from django.urls import path

from user import views


app_name = 'user'  # for reverse fn to reference correctly

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/create/', views.CreateTokenView.as_view(), name='token-create'),
    path('me/', views.ManageUserView.as_view(), name='me'),
]

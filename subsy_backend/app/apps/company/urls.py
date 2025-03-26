"""URL mappings for the company app."""


from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.company import views

app_name = 'apps.company'

router = DefaultRouter()

router.register('companies', views.CompanyViewSet, basename='company')  # prefix is plural companies since appears in actual url, basename is singular company since it's the model name used for internal django reference

urlpatterns = [
    path('', include(router.urls))
]

"""URL mappings for the company app."""


from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.company import views

# from apps.company import views

app_name = 'apps.company'

router = DefaultRouter()

router.register('companies', views.CompanyViewSet, basename='company')


urlpatterns = [
    path('', include(router.urls))
]

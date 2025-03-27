"""Test the application API."""

from venv import create
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Application
from core.tests.shared_data import (
    TEST_APPLICATION_DATA,
    create_user,
    create_application,
    create_company,
)
from utils import pretty_print_json

from ..serializers import ApplicationSerializer


APPLICATIONS_URL = reverse('apps.application:application-list')

def create_detail_url(application_id):
    """Return application detail URL."""
    return reverse('apps.application:application-detail', args=[application_id])



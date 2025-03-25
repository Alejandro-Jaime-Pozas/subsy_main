from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from core.models import Company
from core.views import BaseAuthPermissions
from apps.company.serializers import CompanySerializer


class CompanyViewSet(
    BaseAuthPermissions,
    ModelViewSet,
):
    """Set the main company view set."""
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    # override to only return companies that the user is in
    def get_queryset(self):
        """Return companies that the user is in."""
        return super().get_queryset().filter(users=self.request.user).order_by('pk')

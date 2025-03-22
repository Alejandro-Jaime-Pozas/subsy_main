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

    # override if user is not part of company, return 403 permission denied
    def get_object(self):
        """Raise 403 if user is not part of company."""
        obj = get_object_or_404(Company, pk=self.kwargs['pk'])
        if self.request.user not in obj.users.all():
            raise PermissionDenied('You do not have permission to view this company.', 403)
        return obj

from rest_framework.viewsets import ModelViewSet

from core.models import Company
from core.views import BaseAuthPermissions
from apps.company.serializers import CompanySerializer


class CompanyViewSet(
    BaseAuthPermissions,
    ModelViewSet,
):
    """Set the main company view set."""
    serializer_class = CompanySerializer
    queryset = Company.objects.all().order_by('pk')  # CHANGE TO JUST THIS USER'S COMPANIES

    # def get_queryset(self):
    #     return super().get_queryset()

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.models import Company
from apps.company.serializers import CompanySerializer


# WILL NEED TO MOVE BASEAUTHPERMISSIONS TO A SHARED FILE FOR ALL APPS
class BaseAuthPermissions():
    """Build a base class to set auth and permissions for company views."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class CompanyViewSet(
    BaseAuthPermissions,
    ModelViewSet,
):
    """Set the main company view set."""
    serializer_class = CompanySerializer
    queryset = Company.objects.all().order_by('pk')  # CHANGE TO JUST THIS USER'S COMPANIES

    # def get_queryset(self):
    #     return super().get_queryset()

from rest_framework.mixins import DestroyModelMixin
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.views import BaseAuthPermissions
from core.models import LinkedBank
from apps.linked_bank.serializers import LinkedBankSerializer


class LinkedBankView(
    BaseAuthPermissions,
    DestroyModelMixin,
    ReadOnlyModelViewSet,
):
    """
    Client should be able to use Retrieve, List, Destroy
    operations on the linked bank (plaid item).
    """

    queryset = LinkedBank.objects.all()
    serializer_class = LinkedBankSerializer

    def get_queryset(self):
        """
        Filter the queryset to only show the linked banks (plaid item)
        for the current user's companies.
        """
        user_companies = self.request.user.companies.all()
        return self.queryset.filter(company__in=user_companies).order_by('pk')

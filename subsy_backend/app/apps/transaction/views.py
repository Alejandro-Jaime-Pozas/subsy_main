from rest_framework.viewsets import ReadOnlyModelViewSet

from core.views import BaseAuthPermissions
from core.models import Transaction

from .serializers import TransactionSerializer


class TransactionViewSet(
    BaseAuthPermissions,
    ReadOnlyModelViewSet,
):
    """
    Client should be able to use Retrieve, List
    operations on the linked bank (plaid item).
    """

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        """
        Filter the queryset to only show the linked banks (plaid item)
        for the current user's companies.
        """
        user = self.request.user
        queryset = self.queryset.filter(
            bank_account__linked_bank__company__users=user
        )
        return queryset.order_by('pk')

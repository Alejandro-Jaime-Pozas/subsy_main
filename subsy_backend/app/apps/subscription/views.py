from rest_framework.viewsets import ReadOnlyModelViewSet

from core.views import BaseAuthPermissions
from core.models import Subscription

from .serializers import SubscriptionSerializer


class SubscriptionViewSet(
    BaseAuthPermissions,
    ReadOnlyModelViewSet,
):
    """
    Client should be able to use Retrieve, List
    # operations on the linked bank (plaid item).
    """

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        """
        Filter the queryset to only show the linked banks (plaid item)
        for the current user's companies.
        """
        user = self.request.user
        queryset = self.queryset.filter(
            transactions__bank_account__linked_bank__company__users=user
        )
        return queryset.order_by('pk')

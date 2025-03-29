from rest_framework.viewsets import ModelViewSet

from core.views import BaseAuthPermissions
from core.models import Subscription

from .serializers import SubscriptionSerializer


class SubscriptionViewSet(
    BaseAuthPermissions,
    ModelViewSet,
):
    """
    Client should be able to use all CRUD
    operations on the subscription model
    since subsy could make errors, user
    can fix.
    """

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        """
        Filter the queryset to only show the subscriptions
        for the current user.
        """
        user = self.request.user
        queryset = self.queryset.filter(user=user)
        return queryset.order_by('pk')

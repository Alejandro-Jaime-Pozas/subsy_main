from rest_framework.viewsets import ReadOnlyModelViewSet

from core.models import BankAccount
from core.views import BaseAuthPermissions
from .serializers import BankAccountSerializer


class BankAccountViewSet(BaseAuthPermissions, ReadOnlyModelViewSet):
    """
    Viewset for bank accounts.
    Only allows GET requests.
    """

    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    def get_queryset(self):
        """Filter bank accounts by user."""
        user = self.request.user

        # filter through LinkedBank => Company => User. This uses the field names from the models.py file.
        return self.queryset.filter(linked_bank__company__users=user).order_by('pk')  # switch later to directly ref user in bank account model for performance improvement

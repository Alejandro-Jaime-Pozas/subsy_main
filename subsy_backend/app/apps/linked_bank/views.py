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
        return super().get_queryset().filter(company__in=user_companies)


    # BELOW CHATGPT CODE SHOULD BE REDUNDANT CODE since already in mixins/viewsets
    # def get(self, request, *args, **kwargs):
    #     """
    #     Get the linked bank (plaid item) for the user.
    #     """
    #     return self.retrieve(request, *args, **kwargs)

    # def delete(self, request, *args, **kwargs):
    #     """
    #     Delete the linked bank (plaid item) for the user.
    #     """
    #     linked_bank = self.get_object()
    #     if request.user not in linked_bank.company.users.all():
    #         return self.permission_denied(request)
    #     return self.destroy(request, *args, **kwargs)

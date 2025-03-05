from rest_framework import viewsets
from core.models import (
    User,
    Company,
    LinkedBank,
    BankAccount,
    Transaction,
    Application,
    Subscription,
    Tag,
)
from core.serializers import (
    UserSerializer,
    CompanySerializer,
    LinkedBankSerializer,
    BankAccountSerializer,
    TransactionSerializer,
    ApplicationSerializer,
    SubscriptionSerializer,
    TagSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class LinkedBankViewSet(viewsets.ModelViewSet):
    queryset = LinkedBank.objects.all()
    serializer_class = LinkedBankSerializer


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

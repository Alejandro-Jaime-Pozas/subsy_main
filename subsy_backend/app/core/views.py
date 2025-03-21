from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


# WILL NEED TO MOVE BASEAUTHPERMISSIONS TO A SHARED FILE FOR ALL APPS
class BaseAuthPermissions():
    """Build a base class to set auth and permissions for company views."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

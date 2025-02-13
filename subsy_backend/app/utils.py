from functools import wraps
from django.http import JsonResponse
import random, string

# WRAPPER FUNCTIONS FOR PLAID VIEWS

def validate_access_token(view_func):
    """Wrapper function that checks if user has a valid access token."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        access_token = request.session.get("access_token")
        # print('got access token from request in wrapper fn:', access_token)
        if not access_token:
            return JsonResponse({'error': 'Access token not available.'}, status=403)
        kwargs["access_token"] = access_token
        return view_func(request, *args, **kwargs)
    return wrapper

def random_37_char_string():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=37))

from django.test import TestCase, SimpleTestCase, RequestFactory
from unittest.mock import Mock
from utils import validate_access_token


class TestValidateAccessTokenDecorator(TestCase):
    def setUp(self):
        self.factory = RequestFactory()  # to create mock requests

    def test_access_token_present(self):
        # Mock the request with an access token in the session (change later, remove session)
        request = self.factory.get('/some-url/')  # using the request factory to create a request
        request.session = {"access_token": "valid_token"}

        # Mock the view fn
        view_func = Mock(return_value=Mock())  # mock view func for testing

        # wrap the view with the decorator
        wrapped_view = validate_access_token(view_func)

        # call the wrapped view
        response = wrapped_view(request)

        # ensure the view func is called once
        view_func.assert_called_once_with(request, access_token='valid_token')

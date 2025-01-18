import json
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

    def test_access_token_missing(self):
        request = self.factory.get('/other-url')
        request.session = {'access_token': None}

        view_func = Mock(return_value=Mock())
        wrapped_view = validate_access_token(view_func)
        response = wrapped_view(request)
        response_data = json.loads(response.content)  # this needed to convert response binary data to python dict obj

        view_func.assert_not_called()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response_data, {'error': 'Access token not available.'})


class TestViews(TestCase):
    """Test the views that allow our app to connect to plaid's API."""

    def test_create_link_token_success(self):
        """Test that creating a link token returns a valid token."""
        # set up a http request obj
        # send http request from django to plaid backend
        # return expected status, expected value/type

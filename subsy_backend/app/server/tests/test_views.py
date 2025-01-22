import json, os, time
from django.test import TestCase, SimpleTestCase, RequestFactory
from unittest.mock import Mock, patch
from django.http import JsonResponse

from utils import validate_access_token
from server.views import create_link_token


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

    def setUp(self):
        self.factory = RequestFactory()  # to create mock requests

    @patch('server.views.splaid_client')  # Mock the plaid_client
    def test_create_link_token_success(self, mock_plaid_client):
        """Test that creating a Link token returns a valid Link token."""
        # set up a http request obj
        # send http request from django to plaid backend
        # return expected status, expected value/type
        # Arrange
        mock_response = Mock()
        mock_response.to_dict.return_value = {
            "link_token": "link-sandbox-8def151b-7666-4f67-b1c1-50e0bc24a811",
            "expiration": "2025-01-22T06:43:11Z",
            "request_id": "qHZAELcgO5WW2ax"
        }
        mock_plaid_client.link_token_create.return_value = mock_response

        request = self.factory.get('/create-link-token/')  # Create a mock GET request

        # Act
        response = create_link_token(request)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "link_token": "link-sandbox-8def151b-7666-4f67-b1c1-50e0bc24a811",
                "expiration": "2025-01-22T06:43:11Z",
                "request_id": "qHZAELcgO5WW2ax"
            }
        )
        mock_plaid_client.link_token_create.assert_called_once()

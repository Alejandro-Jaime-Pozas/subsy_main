import json, os, time, plaid
from unittest.mock import Mock, patch

from django.middleware.csrf import get_token
from django.test import TestCase, SimpleTestCase, RequestFactory

from utils import validate_access_token
from server.views import (
    create_link_token,
    exchange_public_token,
    get_balance,
    csrf_token,
)


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

    create_link_token_dict = {
        "link_token": "link-sandbox-8def151b-7666-4f67-b1c1-50e0bc24a811",
        "expiration": "2025-01-22T06:43:11Z",
        "request_id": "qHZAELcgO5WW2ax"
    }

    def setUp(self):
        self.factory = RequestFactory()  # to create mock requests

    # test create_link_token endpoint
    @patch('server.views.plaid_client')  # Mock the plaid_client
    def test_create_link_token_success(self, mock_plaid_client):
        """Test that creating a Link token returns a valid Link token."""
        # Arrange
        mock_response = Mock()
        mock_response.to_dict.return_value = self.create_link_token_dict
        mock_plaid_client.link_token_create.return_value = mock_response

        request = self.factory.get('create_link_token/')  # Create a mock GET request

        # Act
        response = create_link_token(request)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, self.create_link_token_dict)
        mock_plaid_client.link_token_create.assert_called_once()

    @patch('server.views.plaid_client')
    def test_create_link_token_exception(self, mock_plaid_client):
        """Test that creating a link token with wrong input creates exception."""
        # simluate a request that creates an exception
        mock_plaid_client.link_token_create.side_effect = plaid.ApiException(status=400, reason='Test error')

        request = self.factory.get('create_link_token/')  # create mock get request

        response = create_link_token(request)

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Status Code: 400\nReason: Test error\n'})
        mock_plaid_client.link_token_create.assert_called_once()

    # test exchange_public_token endpoint
    @patch('server.views.plaid_client')
    def test_exchange_public_token_success(self, mock_plaid_client):
        """Test that exchanging the public token for an access token is successful."""

        # Arrange
        mock_response = Mock()
        mock_response.to_dict.return_value = {
            "access_token": "access-sandbox-1234"
        }
        mock_plaid_client.item_public_token_exchange.return_value = mock_response

        data = dict()
        data["public_token"] = self.create_link_token_dict.get("link_token")

        request = self.factory.post('exchange_public_token/', data=json.dumps(data), content_type='application/json')
        request.session = {}

        # Act
        response = exchange_public_token(request)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})
        self.assertEqual(request.session["access_token"], "access-sandbox-1234")
        mock_plaid_client.item_public_token_exchange.assert_called_once()

    @patch('server.views.plaid_client')
    def test_exchange_public_token_exception(self, mock_plaid_client):
        """Test that trying to exchange a token invalidly returns exception error."""
        mock_plaid_client.item_public_token_exchange.side_effect = plaid.ApiException(status=400, reason='Test error')
        data = {"public_token": "invalid-token"}

        request = self.factory.post('exchange_public_token/', data=json.dumps(data), content_type='application/json')
        request.session = {}

        response = exchange_public_token(request)

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": 'Status Code: 400\nReason: Test error\n'})
        self.assertIsNone(request.session.get("access_token"))
        mock_plaid_client.item_public_token_exchange.assert_called_once()

    def test_exchange_public_token_invalid_method(self):
        """Test that making an invalid http request returns error."""
        request = self.factory.get('exchange_public_token/')
        response = exchange_public_token(request)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"error": "Invalid request method."})

    # test csrf_token endpoint
    def test_csrf_token_success(self):
        """Test obtaining csrf token is successful."""

        request = self.factory.get('csrf_token/')
        response = csrf_token(request)
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response_data.get('csrfToken'), None)
        self.assertEqual(len(response_data.get('csrfToken')), 64)

    # # test get_balance endpoint
    # @patch('utils.validate_access_token')
    # @patch('server.views.plaid_client')
    # def test_get_balance_success(self):
    #     """Test that getting user bank balance is successful."""
    #     pass

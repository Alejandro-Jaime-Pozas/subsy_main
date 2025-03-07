# """
# Tests for urls.
# """
# from django.test import SimpleTestCase
# from django.urls import reverse, resolve
# from server import views

# class TestUrls(SimpleTestCase):
#     def test_create_link_token_url(self):
#         url = reverse('server:create_link_token')
#         self.assertEqual(resolve(url).func, views.create_link_token)

#     def test_exchange_public_token_url(self):
#         url = reverse('server:exchange_public_token')
#         self.assertEqual(resolve(url).func, views.exchange_public_token)

#     def test_get_balance_url(self):
#         url = reverse('server:get_balance')
#         self.assertEqual(resolve(url).func, views.get_balance)

#     def test_csrf_token_url(self):
#         url = reverse('server:csrf_token')
#         self.assertEqual(resolve(url).func, views.csrf_token)

#     def test_get_latest_transactions_url(self):
#         url = reverse('server:get_latest_transactions')
#         self.assertEqual(resolve(url).func, views.get_latest_transactions)

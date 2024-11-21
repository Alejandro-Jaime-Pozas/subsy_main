"""
Test custom Django management commands.
"""
from unittest.mock import patch

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')  # Command.check is method provided by Command base class we are importing; this allows for accessing the check return value within our class method tests (as patched_check below)
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_ford_db_ready(self, patched_check):
        """Test waiting for database if database is ready."""
        patched_check.return_value = True  # when command is called, just return its value as True, dont do anything else

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):  # in order of called wrapper fns, from inner-most to outer-most level
        """Test waiting for database when getting OperationalError."""
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]  # side_effect allows to handle diff items depending on their data type ie bool vs int vs str; the * 2 and so on done w/trial and error checks of db being ready

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])

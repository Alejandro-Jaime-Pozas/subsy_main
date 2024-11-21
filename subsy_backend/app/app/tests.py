"""
Sample tests
"""
from django.test import SimpleTestCase

from app import example_calc


class CalcTests(SimpleTestCase):
    """Test the example_calc module."""

    def test_add_numbers(self):
        """Test adding numbers together."""
        res = example_calc.add(5, 6)

        self.assertEqual(res, 11)

    def test_subtract_numbers(self):
        """Test subtracting the numbers together."""
        res = example_calc.subtract(15, 10)

        self.assertEqual(res, 5)

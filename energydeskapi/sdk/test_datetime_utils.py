from unittest import TestCase

import pendulum

from energydeskapi.sdk.datetime_utils import parse_date_exactly


class TestDatetimeUtils(TestCase):
    def test_parse_date_exactly(self):
        self.assertEqual(parse_date_exactly("2025-08-10"), pendulum.Date(2025, 8, 10))
        self.assertEqual(parse_date_exactly("2025-08-10 10:12:12"), pendulum.Date(2025, 8, 10))
        with self.assertRaises(Exception):
            parse_date_exactly("2025-08")
        with self.assertRaises(Exception):
            parse_date_exactly(None)



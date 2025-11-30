from unittest import TestCase

from energydeskapi.sdk.common_utils import split_in_chunks


class TestCommonUtils(TestCase):
    def test_split_in_chunks(self):
        self.assertEqual([[1,2,3], [4,5,6], [7]], split_in_chunks([1,2,3,4,5,6,7], 3))
        self.assertEqual([], split_in_chunks([], 3))


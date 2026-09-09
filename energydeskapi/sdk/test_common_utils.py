from unittest import TestCase

from energydeskapi.sdk.common_utils import split_in_chunks, not_nones_in_list, not_nones_in_dict_values, \
    optional_to_list, flatten_nested2_list, optional_map, optional_map_or


class TestCommonUtils(TestCase):
    def test_split_in_chunks(self):
        self.assertEqual([[1,2,3], [4,5,6], [7]], split_in_chunks([1,2,3,4,5,6,7], 3))
        self.assertEqual([], split_in_chunks([], 3))

    def test_not_nones_in_list(self):
        self.assertListEqual(not_nones_in_list([1, 2, None, 3, None, 4]), [1, 2, 3, 4])

    def test_not_nones_in_dict_values(self):
        self.assertDictEqual(not_nones_in_dict_values({'a': 1, 'b': 2, 'c': None, 'd':  3, 'e': None, 'f': 4}), {'a': 1, 'b': 2, 'd': 3, 'f': 4})

    def test_optional_to_list(self):
        self.assertListEqual(optional_to_list(4), [4])
        self.assertListEqual(optional_to_list('ab'), ['ab'])
        self.assertListEqual(optional_to_list(None), [])

    def test_flatten_nested2_list(self):
        self.assertListEqual(flatten_nested2_list([[1,2,3], [4,5,6], [7]]), [1,2,3,4,5,6,7])

    def test_optional_map(self):
        self.assertEqual(optional_map(None, lambda x: x*2), None)
        self.assertEqual(optional_map(3, lambda x: x*2), 6)
        self.assertEqual(optional_map("ciao", lambda x: x.upper()), "CIAO")

    def test_optional_map_or(self):
        self.assertEqual(optional_map_or(None, lambda x: x*2, 4), 4)
        self.assertEqual(optional_map_or(3, lambda x: x*2, 0), 6)
        self.assertEqual(optional_map_or("ciao", lambda x: x.upper(), ""), "CIAO")
        self.assertEqual(optional_map_or(None, lambda x: x.upper(), "BUONASERA"), "BUONASERA")
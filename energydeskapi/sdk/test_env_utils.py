from unittest import TestCase

from energydeskapi.sdk.env_utils import from_semicolon_colon_config_to_dict


class TestEnvUtils(TestCase):
    def test_from_semicolon_colon_config_to_dict(self):
        dc = from_semicolon_colon_config_to_dict("interval_ms:10;chunk_size:50;chunk_pause_ms:1000")
        self.assertDictEqual(dc, {
            "interval_ms": "10",
            "chunk_size": "50",
            "chunk_pause_ms": "1000"
        })

    def test_from_semicolon_colon_config_to_dict_wrong(self):
        self.assertRaises(Exception, from_semicolon_colon_config_to_dict, "interval_ms;chunk_size")

    def test_from_semicolon_colon_config_to_dict_empty(self):
        dc = from_semicolon_colon_config_to_dict("")
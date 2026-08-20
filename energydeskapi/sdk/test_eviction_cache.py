import time

from energydeskapi.sdk.eviction_cache import EvictionCache
from unittest import TestCase

class TestEvictionCache(TestCase):
    def test__evict_old_entries(self):
        cache = EvictionCache(max_size=3)
        cache.put("a", 1)
        time.sleep(0.1)  # Ensure a time difference for eviction
        cache.put("b", 2)
        time.sleep(0.1)  # Ensure a time difference for eviction
        cache.put("c", 3)
        self.assertListEqual(cache.keys_in_cache(), ["a", "b", "c"])
        time.sleep(0.1)  # Ensure a time difference for eviction
        cache.put("d", 4)
        time.sleep(0.1)  # Ensure a time difference for eviction
        self.assertListEqual(cache.keys_in_cache(), ["b", "c", "d"])
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.get("b"), 2)
        self.assertEqual(cache.get("c"), 3)
        self.assertEqual(cache.get("d"), 4)
        time.sleep(0.1)  # Ensure a time difference for eviction
        self.assertListEqual(cache.keys_in_cache(), ["b", "c", "d"])
        self.assertEqual(cache.get("b"), 2)
        cache.put("e", 5)
        self.assertListEqual(cache.keys_in_cache(), ["b", "d", "e"])
        self.assertIsNone(cache.get("c"))
        self.assertEqual(cache.get("b"), 2)
        self.assertEqual(cache.get("d"), 4)
        self.assertEqual(cache.get("e"), 5)
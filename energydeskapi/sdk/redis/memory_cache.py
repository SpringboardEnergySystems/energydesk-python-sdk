# Used for test without REDIS
# Borg Singleton
class MemCache(object):
    _shared_borg_state = {}
    _mem_cache={}
    def __new__(cls, *args, **kwargs):
        obj = super(MemCache, cls).__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_borg_state
        obj.mem_cache=cls._mem_cache
        return obj
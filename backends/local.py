from .base import Backend


class LocalBackend(Backend):
    def __init__(self):
        self.cache = {}

    def __getitem__(self, element_id):
        return self.cache.get(element_id)

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __contains__(self, item):
        return item in self.cache

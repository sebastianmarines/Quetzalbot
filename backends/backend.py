from abc import ABCMeta, abstractmethod


class Backend(metaclass=ABCMeta):
    @abstractmethod
    def __getitem__(self, element_id):
        pass  # pragma: no cover

    @abstractmethod
    def __setitem__(self, key, value):
        pass  # pragma: no cover

    @abstractmethod
    def __contains__(self, item):
        pass  # pragma: no cover


class LocalBackend(Backend):
    def __init__(self):
        self.cache = {}

    def __getitem__(self, element_id):
        return self.cache.get(element_id)

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __contains__(self, item):
        return item in self.cache

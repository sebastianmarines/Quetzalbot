from utils.dom import BackendDOMElement

from .base import Backend


class LocalBackend(Backend):
    def __init__(self):
        self.cache = {}

    def __getitem__(self, element_id) -> BackendDOMElement:
        return self.cache.get(element_id)

    def __setitem__(self, key: str, value: BackendDOMElement):
        self.cache[key] = value

    def __contains__(self, item) -> bool:
        return item in self.cache

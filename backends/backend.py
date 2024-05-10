from abc import ABCMeta, abstractmethod
import requests

class Backend(metaclass=ABCMeta):
    @abstractmethod
    def __getitem__(self, element_id):
        pass

    @abstractmethod
    def __setitem__(self, key, value):
        pass

    @abstractmethod
    def __contains__(self, item):
        pass


class LocalBackend(Backend):
    def __init__(self):
        self.cache = {}

    def __getitem__(self, element_id):
        return self.cache.get(element_id)

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __contains__(self, item):
        return item in self.cache

class RemoteBackend(Backend):
    def __init__(self):
        self.url = "http://localhost:8000"

    def get_active(self):
        active_url = f"{self.url}/fetchActive"
        response = requests.get(active_url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception("There are no active elements")

    def __getitem__(self, element_id):
        active = self.get_active()
        for element in active:
            if element["id"] == element_id:
                return element
        return None

    def __setitem__(self, key, value):
        pass
    def __contains__(self, item):
        pass
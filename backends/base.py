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

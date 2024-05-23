from abc import ABCMeta, abstractmethod

from utils.dom import BackendDOMElement


class Backend(metaclass=ABCMeta):
    @abstractmethod
    def __getitem__(self, element_id) -> BackendDOMElement:
        pass  # pragma: no cover

    @abstractmethod
    def __setitem__(self, key: str, value: BackendDOMElement):
        pass  # pragma: no cover

    @abstractmethod
    def __contains__(self, item) -> bool:
        pass  # pragma: no cover

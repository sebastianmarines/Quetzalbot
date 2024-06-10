from abc import ABCMeta, abstractmethod

from selenium import webdriver

from backends import Backend
from utils.dom import DOMElement


class Healer(metaclass=ABCMeta):
    driver: webdriver.Chrome | webdriver.Firefox
    backend: Backend

    @abstractmethod
    def heal(
        self, previous_element: DOMElement, dom_tree: DOMElement
    ) -> tuple[DOMElement, int]: ...

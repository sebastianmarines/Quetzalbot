from abc import ABCMeta, abstractmethod

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from backend import Backend
from dom import DOMElement, build_dom_tree


class Healer(metaclass=ABCMeta):
    driver: webdriver.Chrome | webdriver.Firefox

    @abstractmethod
    def heal(
        self, element_id: str, previous_element, html_body: str
    ) -> list[tuple[DOMElement, int]]: ...


class FuzzyHealer(Healer):
    tree: DOMElement

    def heal(
        self, element_id: str, previous_element, html_body: str
    ) -> list[tuple[DOMElement, int]]:
        self.tree = build_dom_tree(html_body)
        matches = self.tree.search(previous_element)
        if matches:
            return matches
        raise ValueError(
            f"Element with id '{element_id}' not found in the new DOM tree"
        )

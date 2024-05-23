from abc import ABCMeta, abstractmethod
from typing import Tuple

from fuzzywuzzy import fuzz
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


class FuzzyHealer(Healer):
    tree: DOMElement

    @staticmethod
    def compare_elements(element1: DOMElement, element2: DOMElement) -> int:
        """Compares two DOM elements and returns a similarity score."""
        if element2.tag_name in ["[document]", "html", "head", "body"]:
            return 0

        tag_name_score = fuzz.ratio(element1.tag_name, element2.tag_name)
        attributes_score = fuzz.ratio(
            str(element1.attributes), str(element2.attributes)
        )
        classes_score = fuzz.ratio(
            " ".join(element1.classes), " ".join(element2.classes)
        )
        text_content_score = fuzz.ratio(element1.text_content, element2.text_content)

        return (
            tag_name_score + attributes_score + classes_score + text_content_score
        ) // 4

    def find_best_match(
        self, target: DOMElement, root: DOMElement
    ) -> Tuple[DOMElement, int]:
        """Finds the best match for the target element in the DOM tree rooted at root."""
        best_match = None
        best_score = -1

        def traverse(node: DOMElement):
            nonlocal best_match, best_score

            score = self.compare_elements(target, node)
            if score > best_score:
                best_score = score
                best_match = node

            for child in node.children:
                traverse(child)

        traverse(root)
        if best_match is not None:
            return best_match, best_score
        else:
            raise ValueError("No match found in the DOM tree.")

    def heal(
        self, previous_element: DOMElement, dom_tree: DOMElement
    ) -> tuple[DOMElement, int]:
        match = self.find_best_match(previous_element, dom_tree)
        return match

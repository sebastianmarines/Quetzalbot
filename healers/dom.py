from typing import Tuple

from bs4 import BeautifulSoup, Tag
from fuzzywuzzy import fuzz
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class DOMElement:
    tag_name: str
    children: list["DOMElement"]
    attributes: dict
    classes: list[str]
    text_content: str
    parent: "DOMElement"  # New attribute for parent node

    def __init__(self, tag: Tag, parent: "DOMElement" = None):
        self.tag_name = tag.name
        self.parent = parent  # Set the parent attribute
        self.children = [
            DOMElement(child, self) for child in tag.children if isinstance(child, Tag)
        ]
        self.attributes = {k: v for k, v in tag.attrs.items() if k != "class"}
        self.classes = tag.get("class", [])
        self.text_content = tag.get_text(strip=True)

    def __repr__(self):
        return (
            f"DOMElement(tag_name='{self.tag_name}', children={self.children}, "
            f"attributes={self.attributes}, classes={self.classes}, parent={self.parent.tag_name if self.parent else None})"
        )

    def get_best_selector(self) -> (By, str):
        if self.tag_name in ["body", "html"]:
            return By.TAG_NAME, self.tag_name
        elif self.attributes.get("id"):
            return By.ID, self.attributes["id"]
        elif self.attributes.get("name"):
            return By.NAME, self.attributes["name"]
        elif self.classes:
            return By.CSS_SELECTOR, self._build_css_selector()
        else:
            raise ValueError("Cannot find a suitable selector for the element")

    def _build_css_selector(self) -> str:
        selector = self.tag_name
        for cls in self.classes:
            selector += f".{cls}"
        return selector


def build_dom_tree(html):
    soup = BeautifulSoup(html.replace("\n", " "), "html.parser")
    return DOMElement(soup)  # Assuming we want to start from the body tag


def from_web_element(element: WebElement) -> DOMElement:
    html = element.get_attribute("outerHTML")
    soup = BeautifulSoup(html, "html.parser")
    children = list(soup.children)
    if len(children) != 1:
        raise ValueError("Expected a single root element")
    return DOMElement(children[0])

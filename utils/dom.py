from bs4 import BeautifulSoup, Tag
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class DOMElement:
    tag_name: str
    children: list["DOMElement"]
    attributes: dict
    classes: list[str]
    text_content: str
    parent: "DOMElement"

    def __init__(self, tag: Tag, parent: "DOMElement" = None):
        self.tag_name = tag.name
        self.parent = parent
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


class BackendDOMElement(DOMElement):
    screenshot_bytes: bytes | None
    screenshot_url: str | None
    healed = False
    failed_locator: str | None

    def __init__(
        self, tag: Tag, screenshot: bytes | None = None, parent: "DOMElement" = None
    ):
        super().__init__(tag, parent)
        self.screenshot_bytes = screenshot


def build_dom_tree(html):
    soup = BeautifulSoup(html.replace("\n", " "), "html.parser")
    return DOMElement(soup)


def from_web_element_to_backend_element(element: WebElement) -> BackendDOMElement:
    html = element.get_attribute("outerHTML")
    soup = BeautifulSoup(html, "html.parser")
    children = list(soup.children)
    if len(children) != 1:
        raise ValueError("Expected a single root element")
    return BackendDOMElement(children[0])

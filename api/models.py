from pydantic import BaseModel
from collections import namedtuple

element_t = namedtuple(
    "element",
    ["element", "id", "tag_name", "classes", "text_content", "selector", "attributes"],
)


class Report(BaseModel):
    current_url: str
    element_tag: str
    element_classes: list[str]
    element_text: str
    element_selector: str
    change_failed: str
    change_healed: str
    change_score: float
    url_screenshot: str
    attributes: list[str]


class StatusUpdate(BaseModel):
    success: bool


class HtmlHealing(BaseModel):
    html: str
    prev_element: element_t

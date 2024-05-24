from pydantic import BaseModel


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

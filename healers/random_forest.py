import requests
from bs4 import BeautifulSoup

from api.random_forest import element_t
from healers import Healer
from utils.dom import DOMElement


class RandomForest(Healer):
    backend_url: str

    def __init__(self, backend_url: str):
        self.backend_url = backend_url

    def _exec_remote(self, soup, prev_element: dict) -> str:
        response = requests.post(
            self.backend_url + "/heal/random_forest",
            json={"html": str(soup), "prev_element": list(prev_element)},
            )
        response.raise_for_status()

        return response.text

    def heal(
        self, previous_element: DOMElement, _dom_tree: DOMElement
    ) -> tuple[DOMElement, int]:
        html = self.driver.execute_script("return document.body.outerHTML")
        soup = BeautifulSoup(html.replace("\n", " "), "html.parser")
        elem_id = previous_element.attributes.get("id")
        classes = " ".join(previous_element.classes)
        prev_element = element_t(
            element=(
                f"id={elem_id}"
                if elem_id is not None
                else classes if classes != "" else previous_element.text_content
            ),
            id=elem_id,
            tag_name=previous_element.tag_name,
            classes=classes,
            text_content=previous_element.text_content,
            selector=str(previous_element),
            attributes="".join(
                [f"{k}={v}" for k, v in previous_element.attributes.items()]
            ),
        )

        print("Sent request to backend to heal element")
        new_element = self._exec_remote(soup, prev_element)
        print(f"Received response from backend: {new_element}")

        # TODO parse other selectors

        new_id = new_element.replace("id=", "")

        new_dom_element = DOMElement(tag=None)

        new_dom_element.attributes["id"] = new_id.strip('"')

        return new_dom_element, 0


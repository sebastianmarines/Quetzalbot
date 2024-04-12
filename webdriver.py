import colorlog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
import logging
from typing import Optional

from backends.backend import Backend, LocalBackend
from healers.dom import DOMElement

from selenium.webdriver.remote.webelement import WebElement

from healers.healer import Healer, FuzzyHealer


def get_searchable_string(element: WebElement):
    tag_name = element.tag_name
    classes = element.get_attribute("class")
    if classes is not None:
        classes = classes.split()
    else:
        classes = []
    attributes = element.get_attribute("attributes")
    text_content = element.text
    return f"{tag_name} {' '.join(classes)} {attributes} {text_content}".strip()


class HealingDriver:
    _tree: DOMElement
    _backend: Backend
    _healer: Healer
    driver: webdriver.Chrome | webdriver.Firefox

    def __init__(
        self,
        browser_name="chrome",
        backend: Backend = LocalBackend(),
        healer: Healer = FuzzyHealer(),
    ):
        if browser_name.lower() == "chrome":
            self.driver = webdriver.Chrome()
        elif browser_name.lower() == "firefox":
            self.driver = webdriver.Firefox()
        else:
            raise ValueError(f'Browser "{browser_name}" is not supported!')

        self._logger = colorlog.getLogger(__name__)
        colorlog.basicConfig(level=logging.INFO)
        handler = colorlog.StreamHandler()
        self._logger.addHandler(handler)
        self._logger.propagate = False

        handler.setFormatter(
            colorlog.ColoredFormatter(
                "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s",
                datefmt=None,
                reset=True,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
                secondary_log_colors={},
                style="%",
            )
        )

        self._backend = backend
        self._healer = healer
        self._healer.backend = self._backend
        self._healer.driver = self.driver

    def heal_element(self, element_id: str) -> DOMElement:
        if element_id in self._backend:
            self._logger.info(f"Element with id '{element_id}' found in cache")
            html_body = self.driver.execute_script("return document.body.outerHTML")

            previous_element = self._backend[
                element_id
            ]  # TODO: Currently is the searchable string

            elements = self._healer.heal(element_id, previous_element, html_body)

            if elements:
                element, score = elements[0]
                self._logger.info(
                    f"Element with id '{element_id}' healed successfully"
                    f"\n({score=})"
                    f"\n({element=})"
                )

                return element

        else:
            self._logger.error(f"Healing failed for element with id '{element_id}'")

        raise ValueError(f"Element with id '{element_id}' not found in the new DOM tree")


    def find_element(self, by: str = By.ID, value: Optional[str] = None):
        try:
            element = self.driver.find_element(by, value)
        except NoSuchElementException:
            self._logger.error(
                f"Element with {by}='{value}' not found, trying to heal it"
            )
            if value is None:
                raise NoSuchElementException(f"Element with {by}='{value}' not found")
            element = self.heal_element(value)
            return self.find_element(by, element.attributes["id"])
        else:
            self._backend[value] = get_searchable_string(element)
            return element

    def get(self, url: str):
        self.driver.get(url)
        self._logger.info(f"Current URL: {self.driver.current_url}")

    def __getattr__(self, attr):
        return getattr(self.driver, attr)

    def close(self):
        self.driver.close()

    def quit(self):
        self.driver.quit()

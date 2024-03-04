import colorlog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
import logging

from backend import Backend, LocalBackend
from dom import build_dom_tree, DOMElement

from selenium.webdriver.remote.webelement import WebElement


def get_searchable_string(element: WebElement):
    tag_name = element.tag_name
    classes = element.get_attribute("class").split()
    attributes = element.get_attribute("attributes")
    text_content = element.text
    return f"{tag_name} {' '.join(classes)} {attributes} {text_content}".strip()


class HealingDriver:
    _tree: DOMElement
    _backend: Backend

    def __init__(self, browser_name="chrome", backend: Backend = LocalBackend):
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

        handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        ))

        self._logger.debug("Logger initialized")

        self._backend = backend()

    def heal_element(self, element_id: str):
        if element_id in self._backend:
            self._logger.info(f"Element with id '{element_id}' found in cache")
            body = self.driver.execute_script("return document.body.outerHTML")
            self._tree = build_dom_tree(body)
            previous_element = self._backend[element_id]
            matches = self._tree.search(previous_element)
            if matches:
                self._logger.info(f"Element with id '{element_id}' found")
                self._logger.info(f"{matches[0][0]=}")
                new_id = matches[0][0].attributes["id"]
                new_element = self.get_element_by_id(new_id)
                # Cache the new element
                self._backend[new_id] = get_searchable_string(new_element)
                return new_element
            else:
                self._logger.error(f"Element with id '{element_id}' not found")
                raise
        else:
            self._logger.error(f"Healing failed for element with id '{element_id}'")

    def find_element(self, by: str = By.ID, value: str | None = None):
        self._logger.info(f"Current URL: {self.driver.current_url}")
        try:
            self.driver.find_element(by, value)
        except NoSuchElementException as e:
            self._logger.error(f"Element with {by}='{value}' not found"
                               f"({e.msg})")
            self.heal_element(value)
        else:
            self._logger.info(f"Element with {by}='{value}' found")

            element = self.driver.find_element(by, value)
            self._backend[value] = get_searchable_string(element)
            return element

    def get(self, url: str):
        self.driver.get(url)

    def __getattr__(self, attr):
        return getattr(self.driver, attr)

    def close(self):
        self.driver.close()

    def quit(self):
        self.driver.quit()

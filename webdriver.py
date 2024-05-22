import logging
from dataclasses import dataclass

import colorlog
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from backends import Backend, LocalBackend
from healers.dom import DOMElement, build_dom_tree, from_web_element
from healers.healer import FuzzyHealer, Healer


@dataclass
class Config:
    screenshot_enabled = False
    logging_level = logging.INFO


class HealingDriver:
    _tree: DOMElement
    _backend: Backend
    _healer: Healer
    driver: webdriver.Chrome | webdriver.Firefox
    config: Config

    def __init__(
            self,
            browser_name="chrome",
            backend: Backend = LocalBackend(),
            healer: Healer = FuzzyHealer(),
            config: Config = Config(),
            **kwargs,
    ):
        self.config = config
        if browser_name.lower() == "chrome":
            self.driver = webdriver.Chrome(**kwargs)
        elif browser_name.lower() == "firefox":
            self.driver = webdriver.Firefox(**kwargs)
        else:
            raise ValueError(f'Browser "{browser_name}" is not supported!')

        self._logger = colorlog.getLogger(__name__)
        colorlog.basicConfig(level=config.logging_level)
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

    def heal_element(self, element_selector: str) -> DOMElement:
        if element_selector in self._backend:
            self._logger.info(f"Element with id '{element_selector}' found in cache")
            html_body = self.driver.execute_script("return document.body.outerHTML")

            previous_element = self._backend[
                element_selector
            ]

            dom_tree = build_dom_tree(html_body)
            element, score = self._healer.heal(previous_element, dom_tree)
            self._logger.info(
                f"Element with id '{element_selector}' healed successfully"
                f"\n({score=})"
                f"\n({element=})"
            )

            return element

        else:
            self._logger.error(
                f"Healing failed for element with id '{element_selector}'"
            )

        raise ValueError(
            f"Element with id '{element_selector}' not found in the new DOM tree"
        )

    def find_element(
            self, by: str = By.ID, value: str | None = None, *, healed: bool = False
    ):
        try:
            element = self.driver.find_element(by, value)
        except NoSuchElementException:
            self._logger.error(
                f"Element with {by}='{value}' not found, trying to heal it"
            )
            if value is None:
                raise NoSuchElementException(f"Element with {by}='{value}' not found")
            element = self.heal_element(value)
            new_by, selector = element.get_best_selector()
            if new_by != by:
                self._logger.warning(
                    f"Selector changed from {by}='{value}' to {new_by}='{selector}'"
                )
            return self.find_element(new_by, selector, healed=True)
        else:
            if healed and self.config.screenshot_enabled:
                self._logger.info(
                    f"Taking screenshot of the element with selector {by} = '{value}'"
                )
                outline_style = self.driver.execute_script(
                    "return arguments[0].style.outline", element
                )
                self.driver.execute_script(
                    "arguments[0].style.outline = '#f00 solid 5px';", element
                )
                screenshot_path = "screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                self.driver.execute_script(
                    "arguments[0].style.outline = arguments[1];", element, outline_style
                )

                # TODO: Save the screenshot in the backend

            self._backend[value] = from_web_element(element)
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

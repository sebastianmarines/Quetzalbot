from pathlib import Path
import time

from selenium.webdriver.common.by import By

from backends import RemoteBackend
from healers import FuzzyHealer, RandomForest
from webdriver import HealingDriver


class TestSimple:
    driver: HealingDriver

    def setup_method(self):
        self.driver = HealingDriver(
            backend=RemoteBackend(
                bucket_name="fenix-screenshots-bmkweqjm",
                endpoint="https://fenixqa.tech"
            ),
            healer=RandomForest(backend_url="https://fenixqa.tech"),
        )

    def teardown_method(self):
        self.driver.quit()

    def test_heal_element(self):
        html_file = Path("sample.html").resolve()
        self.driver.get(html_file.as_uri())
        button = self.driver.find_element(By.ID, "btn")
        button.click()
        time.sleep(1)
        text = self.driver.find_element(By.ID, "text")
        assert text.text == "Hello, World!"
        time.sleep(1)

        new_html_file = Path("sample2.html").resolve()
        self.driver.get(new_html_file.as_uri())
        button = self.driver.find_element(By.ID, "btn")
        button.click()
        time.sleep(1)
        self.driver.implicitly_wait(0.1)
        text = self.driver.find_element(By.ID, "text")
        assert text.text == "Found new button!"
        time.sleep(1)

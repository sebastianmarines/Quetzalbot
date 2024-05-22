from pathlib import Path

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from webdriver import HealingDriver


class TestHealingDriver:
    driver: HealingDriver

    def setup_method(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = HealingDriver(options=chrome_options)

    def teardown_method(self):
        self.driver.quit()

    def test_get(self):
        html_file = Path("sample.html").resolve()
        self.driver.get(html_file.as_uri())
        assert self.driver.current_url == html_file.as_uri()

    def test_find_element(self):
        html_file = Path("sample.html").resolve()
        self.driver.get(html_file.as_uri())
        button = self.driver.find_element(By.ID, "btn")
        assert button.get_attribute("id") == "btn"

    def test_click(self):
        html_file = Path("sample.html").resolve()
        self.driver.get(html_file.as_uri())
        button = self.driver.find_element(By.ID, "btn")
        button.click()
        text = self.driver.find_element(By.ID, "text")
        assert text.text == "Hello, World!"

    def test_implicit_wait(self):
        html_file = Path("sample.html").resolve()
        self.driver.get(html_file.as_uri())
        button = self.driver.find_element(By.ID, "btn")
        button.click()
        self.driver.implicitly_wait(0.1)
        text = self.driver.find_element(By.ID, "text")
        assert text.text == "Hello, World!"

    def test_heal_element(self):
        html_file = Path("sample.html").resolve()
        self.driver.get(html_file.as_uri())
        button = self.driver.find_element(By.ID, "btn")
        button.click()
        self.driver.implicitly_wait(0.1)
        text = self.driver.find_element(By.ID, "text")
        assert text.text == "Hello, World!"

        new_html_file = Path("sample2.html").resolve()
        self.driver.get(new_html_file.as_uri())
        button = self.driver.find_element(By.ID, "btn")
        button.click()
        self.driver.implicitly_wait(0.1)
        text = self.driver.find_element(By.ID, "text")
        assert text.text == "Found new button!"

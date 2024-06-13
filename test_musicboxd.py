import time

from selenium.webdriver.common.by import By

from backends import RemoteBackend
from healers import RandomForest, FuzzyHealer
from webdriver import HealingDriver


class TestMusicBoxd:
    driver: HealingDriver

    def setup_method(self):
        self.driver = HealingDriver(
            backend=RemoteBackend(
                bucket_name="fenix-screenshots-bmkweqjm",
                endpoint="https://fenixqa.tech"
            ),
            healer=FuzzyHealer(),
        )
        self.url = "http://localhost:3000/"

    def execute_flow(self, path, button_id):
        self.driver.get(self.url + path)
        time.sleep(1)
        button = self.driver.find_element(By.ID, button_id)
        for _ in range(5):
            button.click()
            time.sleep(1)

    def test_click_button(self):
        self.execute_flow("songs.html", "next-btn")
        self.execute_flow("songs2.html", "next-btn")

        self.driver.close()

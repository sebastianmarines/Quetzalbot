import time

from webdriver import HealingDriver
from selenium.webdriver.common.by import By
from pathlib import Path

driver = HealingDriver()

html_file = Path("sample.html").resolve()

driver.get(html_file.as_uri())
driver.find_element(By.ID, "btn")

new_html_file = Path("sample2.html").resolve()
driver.get(new_html_file.as_uri())
driver.find_element(By.ID, "btn")

driver.quit()

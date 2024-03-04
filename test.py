import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from webdriver import HealingDriver
from selenium.webdriver.common.by import By
from pathlib import Path

driver = HealingDriver()

html_file = Path("sample.html").resolve()

driver.get(html_file.as_uri())
button = driver.find_element(By.ID, "btn")
button.click()
driver.implicitly_wait(0.1)
text = driver.find_element(By.ID, "text")
assert text.text == "Hello, World!"

new_html_file = Path("sample2.html").resolve()
driver.get(new_html_file.as_uri())
button = driver.find_element(By.ID, "btn")
button.click()
driver.implicitly_wait(0.1)
text = driver.find_element(By.ID, "text")
assert text.text == "Found new button!"

driver.find_element(By.ID, "non-existing-element")

driver.quit()

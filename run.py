import time
from pathlib import Path

from selenium.webdriver.common.by import By

from webdriver import HealingDriver
from selenium import webdriver

# driver = HealingDriver()
# driver = webdriver.Chrome()
nodeURL = "http://localhost:8085"

options = webdriver.ChromeOptions()
options.add_argument("--headless")

driver = webdriver.Remote(
    command_executor=nodeURL,
    options=options,
)

print("Driver is ready")
html_file = Path("sample.html").resolve()
# driver.get(html_file.as_uri())
driver.get("https://sebastianmarines.com/test_html/sample.html")
print("Loaded page")
button = driver.find_element(By.ID, "btn")
button.click()
driver.implicitly_wait(0.1)
text = driver.find_element(By.ID, "text")
assert text.text == "Hello, World!"

new_html_file = Path("sample2.html").resolve()
# driver.get(new_html_file.as_uri())
driver.get("https://sebastianmarines.com/test_html/sample2.html")
button = driver.find_element(By.ID, "btn")
button.click()
driver.implicitly_wait(0.1)
text = driver.find_element(By.ID, "text")
assert text.text == "Found new button!"

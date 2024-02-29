import time

import selenium
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from pathlib import Path

from selenium.webdriver.remote.webelement import WebElement

from dom import DOMElement, build_dom_tree

driver = webdriver.Chrome()

cache: dict[str, WebElement] = {}


def get_searchable_string(element: WebElement):
    tag_name = element.tag_name
    classes = element.get_attribute("class").split()
    attributes = element.get_attribute("attributes")
    text_content = element.text
    return f"{tag_name} {' '.join(classes)} {attributes} {text_content}".strip()


def get_element_by_id(element_id: str):
    try:
        element = driver.find_element(By.ID, element_id)
    except NoSuchElementException:
        print(f"Element with id '{element_id}' not found")
        if element_id in cache:
            print(f"Element with id '{element_id}' found in cache")
            body = driver.execute_script("return document.body.outerHTML")
            tree = build_dom_tree(body)
            previous_element = cache[element_id]
            matches = tree.search(previous_element)
            if matches:
                print(f"Element with id '{element_id}' found")
                print(f"{matches[0][0]=}")
                new_id = matches[0][0].attributes['id']
                new_element = get_element_by_id(new_id)
                # Cache the new element
                cache[new_id] = get_searchable_string(new_element)
                return new_element
            else:
                print(f"Element with id '{element_id}' not found")
                raise

    else:
        print(f"Element with id '{element_id}' found")
        # Cache the element
        cache[element_id] = get_searchable_string(element)
        return element


html_file = Path("sample.html").resolve()
driver.get(html_file.as_uri())

button = get_element_by_id("btn")
time.sleep(2)
button.click()
time.sleep(2)

new_html_file = Path("sample2.html").resolve()
driver.get(new_html_file.as_uri())

button = get_element_by_id("btn")
time.sleep(2)
button.click()
time.sleep(2)

driver.quit()

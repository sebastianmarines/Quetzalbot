from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from healers.dom import DOMElement, from_web_element


class TestDOMElement:
    def setup_method(self):
        self.soup = BeautifulSoup(
            '<div id="1" class="button btn">Hello</div>', "html.parser"
        )
        self.dom_element = DOMElement(self.soup.div)

    def test_dom_element_initialization(self):
        assert self.dom_element.tag_name == "div"
        assert self.dom_element.attributes == {"id": "1"}
        assert self.dom_element.classes == ["button", "btn"]
        assert self.dom_element.text_content == "Hello"

    def test_generate_css_selector(self):
        selector = self.dom_element._build_css_selector()
        assert selector == "div.button.btn"

    def test_from_web_element(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        html = """
        <html>
        <body>
        <button id="btn" class="btn btn-large">Click me</button>
        </body>
        </html>
        """

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("data:text/html," + html)
        element = driver.find_element("id", "btn")
        result = from_web_element(element)
        assert result.tag_name == "button"

from bs4 import BeautifulSoup
from healers.dom import DOMElement, from_web_element
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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

    def test_get_searchable_string(self):
        searchable_string = self.dom_element.get_searchable_string()
        assert searchable_string == "div button btn 1 Hello"

    def test_search(self):
        matches = self.dom_element.search("Hello")
        assert len(matches) == 1
        assert matches[0][0] == self.dom_element
        assert matches[0][1] >= 75

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

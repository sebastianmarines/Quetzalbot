import pytest
from bs4 import BeautifulSoup
from healers.dom import DOMElement

class TestDOMElement:
    def setup_method(self):
        self.soup = BeautifulSoup('<div class="test" id="1">Hello</div>', 'html.parser')
        self.dom_element = DOMElement(self.soup.div)

    def test_dom_element_initialization(self):
        assert self.dom_element.tag_name == 'div'
        assert self.dom_element.attributes == {'id': '1'}
        assert self.dom_element.classes == ['test']
        assert self.dom_element.text_content == 'Hello'

    def test_get_searchable_string(self):
        searchable_string = self.dom_element.get_searchable_string()
        assert searchable_string == 'div test 1 Hello'

    def test_search(self):
        matches = self.dom_element.search('Hello')
        assert len(matches) == 1
        assert matches[0][0] == self.dom_element
        assert matches[0][1] >= 75
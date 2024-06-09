from bs4 import Tag

from healers import FuzzyHealer
from utils.dom import DOMElement, build_dom_tree


class TestHealer:
    def setup_method(self):
        self.healer = FuzzyHealer()
        self.html_body = """
        <html>
            <body>
                    <div id="5" class="test">Hello</div>
                    <div id="2" class="test">World</div>
                    <div id="3" class="test">!</div>
                    <div class="test prueba">Hello world</div>
            </body>
        </html>
        """
        self.dom_tree = build_dom_tree(self.html_body)

        self.html_body2 = """
        <html>
          <head>
            <title>Sample</title>
          </head>
          <body>
            <span id="text"></span>
            <!--    <button id="btn2" class="btn btn-large">Click me 2</button>-->
            <button class="btn btn-large">Click me 2</button>
            <button>Hello</button>
            <div class="div1">
                <button id="btn2" class="btn btn-large">Click me 2</button>
            </div>
            <script>
              const btn = document.getElementById("btn2");
              btn.addEventListener("click", function () {
                const text = document.getElementById("text");
                text.innerHTML = "Found new button!";
              });
            </script>
          </body>
        </html>
        """
        self.dom_tree2 = build_dom_tree(self.html_body2)

    def test_find_by_id(self):
        tag = Tag(name="div", attrs={"id": "1"})
        tag.string = "Hello"
        past_element = DOMElement(tag)

        element, score = self.healer.heal(past_element, self.dom_tree)
        assert element.attributes.get("id") == "5"

    def test_find_by_css_selector(self):
        tag = Tag(name="div")
        tag.string = "Hello world"
        past_element = DOMElement(tag)
        past_element.classes = ["test"]
        element, score = self.healer.heal(past_element, self.dom_tree)
        assert element.text_content == "Hello world"

    def test_find_deeply_nested(self):
        tag = Tag(name="button", attrs={"id": "btn"})
        tag.string = "Click me"
        past_element = DOMElement(tag)
        past_element.classes = ["btn", "btn-large"]
        element, score = self.healer.heal(past_element, self.dom_tree2)
        assert element.text_content == "Click me 2"

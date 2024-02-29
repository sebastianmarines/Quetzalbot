from bs4 import BeautifulSoup, Tag
from fuzzywuzzy import fuzz


class DOMElement:
    tag_name: str
    children: list['DOMElement']
    attributes: dict
    classes: list[str]
    text_content: str

    def __init__(self, tag):
        self.tag_name = tag.name
        self.children = [DOMElement(child) for child in tag.children if isinstance(child, Tag)]
        self.attributes = dict(tag.attrs)
        self.classes = tag.get('class', [])
        self.text_content = tag.get_text(strip=True)

    def __repr__(self):
        return f"DOMElement(tag_name='{self.tag_name}', children={self.children}, attributes={self.attributes}, classes={self.classes})"

    def get_searchable_string(self):
        # Gather all searchable text from the element
        texts = [self.tag_name] + self.classes + [str(value) for key, value in self.attributes.items()] + [
            self.text_content]
        return ' '.join(texts).strip()

    def search(self, query, threshold=75) -> list[tuple['DOMElement', int]]:
        matches = []

        # Search in the current element
        current_string = self.get_searchable_string()
        score = fuzz.partial_ratio(query.lower(), current_string.lower())
        if score >= threshold:
            matches.append((self, score))

        # Recursive search in children
        for child in self.children:
            matches.extend(child.search(query, threshold))

        # Return all matches ordered by their score
        return sorted(matches, key=lambda x: x[1], reverse=True)


def build_dom_tree(html):
    soup = BeautifulSoup(html.replace("\n", " "), 'html.parser')
    return DOMElement(soup)  # Assuming we want to start from the body tag

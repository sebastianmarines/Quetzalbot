from datetime import datetime

from sqlmodel import Session, create_engine, select

from api.db import Attribute, Change, Element, Page

sqlite_file_name = "database.db"
db_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(db_url, echo=True)


def save_page(url):
    new_page = Page(path_html=url)
    with Session(engine) as session:
        session.add(new_page)
        session.commit()
    return new_page.id


def save_element(
    element_tag, element_classes, element_text, element_selector, saved_page
):
    new_element = Element(
        tag_name=element_tag,
        classes=str(element_classes),
        text_content=element_text,
        selector=element_selector,
        page_id=saved_page,
        active=True,
    )
    with Session(engine) as session:
        session.add(new_element)
        session.commit()
        session.refresh(new_element)

        return new_element.id_element


def save_attributes(attributes, saved_element):
    for attribute in attributes:
        new_attribute = Attribute(attr_name=attribute, element_id=saved_element)
        with Session(engine) as session:
            session.add(new_attribute)
            session.commit()


def save_change(
    change_failed, change_healed, change_score, url_screenshot, saved_element
):
    new_chage = Change(
        sel_date=datetime.now().date(),
        sel_time=datetime.now().time(),
        failed_locator=change_failed,
        healed_locator=change_healed,
        score=change_score,
        url_screenshot=url_screenshot,
        elem_id=saved_element,
    )
    with Session(engine) as session:
        session.add(new_chage)
        session.commit()


def save_status():
    pass


# This function is not used - this part was for filling the table
def fill_csv(conn, df):
    cursor = conn.cursor()
    for index, row in df.iterrows():
        insert_query = """
        INSERT INTO change (sel_date, sel_time, failed_locator, healed_locator, score, url_screenshot, elem_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            row["Date"],
            row["Time"],
            row["Failed Locator"],
            row["Healed Locator"],
            row["Score"],
            row["Screenshot"],
            row["Id"],
        )
        cursor.execute(insert_query, values)
    conn.commit()


def fill_element(conn):
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO element (tag_name, classes, text_content, selector, page_id, active)
        VALUES ("com.epam.healenium.selenium.search.locators.XPathStrategy.doAction()", "classes", "Element text", "selector", 1, True)
        """
    cursor.execute(insert_query)
    conn.commit()

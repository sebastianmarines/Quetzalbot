from datetime import date, time
from typing import Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

from api.settings import Settings


class User(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str
    email: str


class Page(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, nullable=False, default=None)
    path_html: str


class Element(SQLModel, table=True):
    id_element: Optional[int] = Field(primary_key=True, nullable=False, default=None)
    tag_name: str = Field(index=True)
    classes: str
    text_content: str
    selector: str
    active: bool
    attributes: list["Attribute"] = Relationship(back_populates="element")
    page_id: Optional[int] = Field(default=None, foreign_key="page.id")


class Attribute(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, nullable=False, default=None)
    attr_name: str = Field(index=True)
    element_id: Optional[int] = Field(default=None, foreign_key="element.id_element")
    element: Optional[Element] = Relationship(back_populates="attributes")


class Change(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, nullable=False, default=None)
    sel_date: date
    sel_time: time
    failed_locator: str
    healed_locator: str
    score: float
    url_screenshot: str
    elem_id: Optional[int] = Field(default=None, foreign_key="element.id_element")


db_url = Settings().db_url

engine = create_engine(db_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        page = session.get(Page, 1)
        if not page:
            page = Page(path_html="https://fenixqa.tech")
            session.add(page)
            session.commit()


create_db_and_tables()

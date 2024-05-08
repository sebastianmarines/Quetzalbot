from sqlmodel import Field, Relationship, Session, SQLModel, create_engine
from typing import Optional
from datetime import date, time


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


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


create_db_and_tables()

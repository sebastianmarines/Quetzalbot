from jinja2 import Environment, FileSystemLoader

from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI
from typing import List
from api.db import Change, Element

from pydantic import BaseModel
from sqlmodel import Session, select
from api.database_handling import (
    save_page,
    save_element,
    save_attributes,
    save_change,
    save_status,
    engine,
)
import pandas as pd

env = Environment(loader=FileSystemLoader("."))

app = FastAPI()
app.mount("/static", StaticFiles(directory="styles"), name="static")


@app.get("/", response_class=HTMLResponse)
async def new_app():
    with Session(engine) as session:
        statement = select(Change, Element).join(Element, isouter=True)
        reports = session.exec(statement).fetchall()
        template = env.get_template("demoreports.html")
        output = template.render(reports=reports)
        return HTMLResponse(content=output)


class Report(BaseModel):
    current_url: str
    element_tag: str
    element_classes: List[str]
    element_text: str
    element_selector: str
    change_failed: str
    change_healed: str
    change_score: str
    url_screenshot: str
    attributes: List[str]


@app.get("/change", response_model=List[Report])
async def receive_report(report: Report):
    saved_page = save_page(report.current_url)
    saved_element = save_element(
        report.element_tag,
        report.element_classes,
        report.element_text,
        report.element_selector,
        saved_page,
    )
    save_attributes(report.attributes, saved_element)
    save_change(
        report.change_failed,
        report.change_healed,
        report.change_score,
        report.url_screenshot,
        saved_element,
    )


class StatusUpdate(BaseModel):
    success: bool


@app.put("/newstatus/{elem_id}")
async def update_status(elem_id: int, status_update: StatusUpdate):
    with Session(engine) as session:
        element = session.get(Element, elem_id)
        if element:
            element.active = status_update.success
            session.commit()
            return {"message": "Status updated successfully"}
        else:
            return {"error": "Element not found"}


@app.get("/download")
async def download_csv():
    with Session(engine) as session:
        statement = select(Change, Element).join(Element, isouter=True)
        reports = session.exec(statement).fetchall()
    df_rows = []
    for change, element in reports:
        row = [
            change.id,
            change.sel_date,
            change.sel_time,
            change.failed_locator,
            change.healed_locator,
            change.score,
            change.url_screenshot,
            element.id_element,
            element.tag_name,
            element.classes,
            element.text_content,
            element.selector,
            element.active,
        ]
        df_rows.append(row)
    df = pd.DataFrame(df_rows)
    print(df)
    csv_file = df.to_csv(index=False)
    response = Response(content=csv_file)
    response.headers["Content-Disposition"] = "attachment; filename=reports.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


@app.get("/fetchActive")
async def send_active():
    with Session(engine) as session:
        statement = select(Element).where(Element.active == 1)
        elements = session.exec(statement).fetchall()
        active_elements = [
            {
                "id": element.id_element,
                "tag_name": element.tag_name,
                "classes": element.tag_name,
                "text_content": element.text_content,
                "page": element.page_id,
            }
            for element in elements
        ]
    return active_elements

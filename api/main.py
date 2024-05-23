import logging
from datetime import datetime
from typing import List

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from sqlmodel import Session, col, select

from api.database_handling import (
    engine,
    save_attributes,
    save_change,
    save_element,
    save_page,
    save_status,
)
from api.db import Change, Element
from api.models import Report, StatusUpdate

logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader("."))
env.filters["fmt_time"] = lambda v: str(v).split(".")[0]

app = FastAPI()
app.mount("/static", StaticFiles(directory="styles"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    with Session(engine) as session:
        statement = (
            select(Change, Element)
            .order_by(col(Change.sel_date).desc())
            .order_by(col(Change.sel_time).desc())
            .join(Element, isouter=True)
        )
        reports = session.exec(statement).fetchall()
        template = env.get_template("dashboard.html.jinja2")
        output = template.render(reports=reports)
        return HTMLResponse(content=output)


@app.post("/change", response_model=Report)
async def receive_report(report: Report):
    # saved_page = save_page(report.current_url)
    saved_element = save_element(
        report.element_tag,
        report.element_classes,
        report.element_text,
        report.element_selector,
        1,
    )
    save_attributes(report.attributes, saved_element)
    if report.change_healed:
        save_change(
            report.change_failed,
            report.change_healed,
            report.change_score,
            report.url_screenshot,
            saved_element,
        )

    return report


@app.put("/new_status/{elem_id}")
async def update_status(elem_id: int, status_update: StatusUpdate):
    """
    Enable or disable an element in the database
    """
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


@app.get("/fetch_active")
async def fetch_active() -> list[Element]:
    with Session(engine) as session:
        statement = select(Element).where(Element.active == 1)
        elements = session.exec(statement).fetchall()
    return elements

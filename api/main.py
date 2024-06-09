import logging
import sys

import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from sqlmodel import Session, col, select

from api.database_handling import engine, save_attributes, save_change, save_element
from api.db import Change, Element
from api.models import Report, StatusUpdate

from .utils import send_notification

EMAIL = "sebastian0marines@gmail.com"

env = Environment(loader=FileSystemLoader("."))
env.filters["fmt_time"] = lambda v: str(v).split(".")[0]

app = FastAPI()
app.mount("/static", StaticFiles(directory="styles"), name="static")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter(
    "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
)
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

logger.info("API is starting up")


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
    logger.info("CSV file created")
    response = Response(content=csv_file)
    response.headers["Content-Disposition"] = "attachment; filename=reports.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


@app.post("/change", response_model=Report)
async def receive_report(report: Report):
    saved_element = save_element(
        report.element_tag,
        report.element_classes,
        report.element_text,
        report.element_selector,
        1,  # TODO: hardcoded
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
        send_notification(EMAIL, report)

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


@app.get("/fetch_active")
async def fetch_active() -> list[Element]:
    with Session(engine) as session:
        statement = select(Element).where(Element.active == 1)
        elements = session.exec(statement).fetchall()
    return list(elements)


@app.get("/{elem_id}", response_model=Element)
async def get_element(elem_id: int):
    with Session(engine) as session:
        element = session.get(Element, elem_id)
        return element

import logging

import boto3
import requests

from api.models import Report
from utils import generate_random_filename
from utils.dom import BackendDOMElement

from .base import Backend


class RemoteBackend(Backend):
    def __init__(self):
        self.bucket_name = "fenix-screenshots-abk1249mx"
        self.s3_client = boto3.client("s3")
        self.cache = {}

    def _fetch(self): ...

    def __getitem__(self, element_id) -> BackendDOMElement:
        return self.cache.get(element_id)

    def __setitem__(self, key: str, value: BackendDOMElement):
        screenshot_url = ""
        file_key = generate_random_filename()
        if value.screenshot_bytes:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=value.screenshot_bytes,
            )
            screenshot_url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"

        report = Report(
            current_url="null",
            element_tag=value.tag_name,
            element_classes=value.classes,
            element_text=value.text_content,
            element_selector=value.get_best_selector()[1],
            change_failed=value.failed_locator,
            change_healed=value.new_locator,
            change_score=0.75,
            attributes=list(value.attributes.keys()),
            url_screenshot=screenshot_url,
        )

        json = report.model_dump()
        response = requests.post("https://fenixqa.tech/change", json=json)
        response.raise_for_status()
        self.cache[key] = value

    def __contains__(self, item) -> bool:
        return item in self.cache

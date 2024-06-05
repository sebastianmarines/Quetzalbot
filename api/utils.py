from datetime import datetime

import boto3

from api.models import Report

client = boto3.client("ses")


def send_notification(to: str, report: Report):
    res = client.send_email(
        Source="notifications@fenixqa.tech",
        Destination={"ToAddresses": [to]},
        Message={
            "Subject": {
                "Data": f"FenixQA healing report {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            },
            "Body": {
                "Html": {
                    "Data": f"""
                    <p> A new element has been healed. </p>
                    <h2> Element </h2>
                    <p> Failed locator: {report.change_failed} </p>
                    <p> Healed locator: {report.change_healed} </p>
                    <p> Score: {report.change_score} </p>
                    <img src="{report.url_screenshot}" alt="Element screenshot" width="600px" />
                    
                    <p> If you want to disable this element, click <a href="https://fenixqa.tech/">here</a> </p>

                    <p> FenixQA </p>
                    """
                }
            },
        },
    )

    if res["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return

    raise Exception("Error sending email")
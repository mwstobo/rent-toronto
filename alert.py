"""Notify users about matched listings"""
import datetime
from typing import List

import boto3

import config
import scraper

SES = boto3.client("ses")


def generate_body(adverts: List[scraper.Advert]) -> str:
    """Generate an email body from a list of adverts"""
    table = "<table>"
    table += "<tr>"
    table += "<th>Category</th>"
    table += "<th>Price</th>"
    table += "<th>Address</th>"
    table += "<th>Distance</th>"
    table += "<th>Link</th>"
    table += "</tr>"
    for advert in adverts:
        link = "<a href='{}'>Link</a>".format(advert.url)
        row = "<tr>"
        row += "<td>{}</td>".format(advert.category)
        row += "<td>{}</td>".format(advert.price)
        row += "<td>{}</td>".format(advert.address)
        row += "<td>{:.2f}km</td>".format(advert.distance)
        row += "<td>{}</td>".format(link)
        row += "</tr>"
        table += row
    table += "</table>"
    return table


def send(adverts: List[scraper.Advert]) -> None:
    """Send an email containing the found adverts"""
    sorted_adverts = sorted(adverts, key=lambda a: a.distance)
    body = generate_body(sorted_adverts)

    destination = {
        "ToAddresses": config.TO_ADDRESSES,
    }

    message = {
        "Subject": {
            "Data": "New apartments for {}".format(datetime.date.today()),
            "Charset": "UTF-8",
        },
        "Body": {
            "Html": {
                "Data": body,
                "Charset": "UTF-8",
            }
        },
    }

    SES.send_email(
        Source=config.FROM_ADDRESS,
        Destination=destination,
        Message=message)

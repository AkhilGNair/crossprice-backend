import json
from functools import partial
from pathlib import Path

from bs4 import BeautifulSoup

from common import PATH_DATA, log, urls


def make_path(name: str, ext: str) -> Path:
    return PATH_DATA / ext / f"{name}.{ext}"


html_path = partial(make_path, ext="html")
json_path = partial(make_path, ext="json")


def clean_text(text: str) -> str:
    return text.strip("\n").strip(" ")


for name, config in urls.items():
    html = BeautifulSoup(html_path(name).read_text(), features="html.parser")
    html_table = html.select_one(config["selector"])

    headers = [
        clean_text(elem.text)
        for elem in html_table.select_one("thead").select("th")
    ]

    body = [
        [clean_text(cell.text) for cell in row.select("td")]
        for row in html_table.select("tbody > tr")
    ]

    log.info("Writing json for %s", name)
    data = [dict(zip(headers, row)) for row in body]
    Path(json_path(name)).write_text(json.dumps(data, indent=2))

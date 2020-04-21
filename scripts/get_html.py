"""
Ported from https://github.com/chendaniely/animal_crossing/blob/master/scripts/acnh/01-get_data.R   # noqa: E501
"""

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import requests

from common import PATH_DATA, log, urls


def phantomjs_html(url: str, name: str) -> str:
    """
    Generates a phantomjs script which will help scrape the html.
    The html would otherwise not be scrapped as it is dynamically generated
    with javascript
    """
    path = PATH_DATA / "html" / f"{name}.html"

    phantomjs_script = textwrap.dedent(
        f"""
        var webPage = require('webpage');
        var page = webPage.create();
        var fs = require('fs');
        var path = '{path}'
        page.open('{url}', function (status) {{
            var content = page.content;
            fs.write(path, content, 'w')
            phantom.exit();
        }});
        """
    )

    return phantomjs_script


def run_phantom_script(url: str, name: str) -> None:
    """
    Creates a tempfile of the javascript code and calls phantomjs to run it
    """

    # Check the page responds
    response = requests.get(url)
    response_code = response.status_code
    if response_code != 200:
        log.error("Got %d from %s", response_code, url)
        sys.exit(1)

    tmpfile = tempfile.NamedTemporaryFile()
    Path(tmpfile.name).write_text(phantomjs_html(url, name))
    subprocess.call(f"phantomjs {tmpfile.name}", shell=True)


for name, data in urls.items():
    log.info("Getting html for %s", name)
    run_phantom_script(url=data["url"], name=name)

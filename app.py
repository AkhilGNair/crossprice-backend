# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
from typing import List
import logging
from logging import FileHandler, Formatter
from pathlib import Path
from werkzeug.routing import BaseConverter

import jinja2
from flask import Flask, render_template, jsonify

# ----------------------------------------------------------------------------#
# Critters
# ----------------------------------------------------------------------------#

DEFAULT_FIELDS = ["Name", "Price", "Image"]

# Read all critters in preserving region and critter type
data = {
    name.stem: json.loads(Path(name).read_text())
    for name in Path("data/json").iterdir()
}

# TODO: Add region and critter type
critters: List[dict] = [critter for _, l in data.items() for critter in l]

clean_critters: str = json.dumps(
    [
        {k: v for k, v in critter.items() if k in DEFAULT_FIELDS}
        for critter in critters
    ]
)

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)

_js_escapes = {
    "\\": "\\u005C",
    "'": "\\u0027",
    '"': "\\u0022",
    ">": "\\u003E",
    "<": "\\u003C",
    "&": "\\u0026",
    "=": "\\u003D",
    "-": "\\u002D",
    ";": "\\u003B",
    "\u2028": "\\u2028",
    "\u2029": "\\u2029",
}
# Escape every ASCII character with a value less than 32.
_js_escapes.update(("%c" % z, "\\u%04X" % z) for z in range(32))


def jinja2_escapejs_filter(value):
    escaped = "".join(
        _js_escapes[letter] if letter in _js_escapes else letter
        for letter in value
    )
    return jinja2.Markup(escaped)

app.jinja_env.filters["escapejs"] = jinja2_escapejs_filter

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def home():
    return render_template("pages/home.html", critters=clean_critters)


@app.route("/api/v1/critters", methods=['GET'])
def get_critters():
    return jsonify(
        [
            {k: v for k, v in critter.items() if k in DEFAULT_FIELDS}
            for critter in critters
        ]
    )

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    return render_template("errors/500.html"), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

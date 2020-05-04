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

_DEFAULT_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}

# ----------------------------------------------------------------------------#
# Critters
# ----------------------------------------------------------------------------#

DEFAULT_FIELDS = ["Name", "Price", "Image"]

# Read all critters in preserving region and critter type
data = {
    name.stem: json.loads(Path(name).read_text())
    for name in Path("data/json").iterdir()
}


def index_critters(data: dict) -> dict:
    return {
        tuple(filename.split("_")): critters
        for filename, critters in data.items()
    }


critters = index_critters(data)

# Tidy tuesday data too!
column_aliases = {"name": "Name", "sell_value": "Price", "image_url": "Image"}
items = json.loads(Path("data/tidytuesday-items.json").read_text())
item_groups = {item["grouping"] for item in items}


# WARN: Deprecated - used for flask app
clean_critters: str = json.dumps(
    [
        {k: v for k, v in critter.items() if k in DEFAULT_FIELDS}
        for _, critters in data.items()
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


@app.route("/api/v1/critters", methods=["GET"])
def get_critters():
    return get_regional_critters("n")


@app.route("/api/v2/critters/region/<string:region>", methods=["GET"])
def get_regional_critters(region: str):

    # Filter files for correct region
    regional = {k: v for k, v in critters.items() if region in k}

    response_data = [
        {k: v for k, v in critter.items() if k in DEFAULT_FIELDS}
        for _, critterset in regional.items()
        for critter in critterset
    ]

    response = jsonify(response_data)
    response.headers.update(_DEFAULT_HEADERS)
    return response


@app.route("/api/v2/items/groups", methods=["GET"])
def get_item_groups():
    """ Returns the high level categories for items."""
    response = jsonify(list(item_groups))
    response.headers.update(_DEFAULT_HEADERS)
    return response


@app.route("/api/v2/items/group/<string:group>", methods=["GET"])
def get_items(group: str):
    """ Returns all the items in a high level category."""

    group = group.lower()

    if group not in item_groups:
        return jsonify({"message": f"{group} not a valid group"}), 400

    items_in_group = (item for item in items if item["grouping"] == group)
    items_in_group_slim = [
        {
            column_aliases[k]: v
            for k, v in item.items()
            if column_aliases.get(k, k) in DEFAULT_FIELDS
        }
        for item in items_in_group
    ]

    # Tidy tuesday list can be non-unique due to sources
    response_data = list(
        {item["Name"]: item for item in items_in_group_slim}.values()
    )

    response = jsonify(response_data)
    response.headers.update(_DEFAULT_HEADERS)
    return response


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

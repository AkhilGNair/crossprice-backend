import json
import logging
import sys
from pathlib import Path

# Project root
PATH_ROOT = Path(__file__).parents[1]


def init_logger():
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [in %(pathname)s:%(lineno)d] [%(levelname)8s]: %(message)s"  # noqa: E501
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    log.addHandler(handler)
    return log


log = init_logger()

PATH_DATA = PATH_ROOT / "data"
urls = json.loads((PATH_DATA / "urls.json").read_text())

# TODO: Pick all relevant object sets
CRITTERS = (
    "acnh_fish_n",
    "acnh_fish_s",
    "acnh_bugs_n",
    "acnh_bugs_s",
)

urls = {k: v for k, v in urls.items() if k in CRITTERS}

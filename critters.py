critters = [
    {"animal": "cat", "price": 900},
    {"animal": "dog", "price": 1200},
    {"animal": "cats and dogs", "price": 900},
    {"animal": "dogs and rats", "price": 12},
]

import json
from pathlib import Path

critters = json.loads(Path("data/acnh_fish_n.json").read_text())

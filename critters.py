import json
from pathlib import Path


critters = json.loads(Path("data/acnh_fish_n.json").read_text())

critters = json.dumps(
    [
        {k: v for k, v in critter.items() if k in ("Name", "Price", "Image")}
        for critter in critters
    ]
)

"""Extract all 9 diagram JSONs to individual files for export."""
import json
import sys
sys.path.insert(0, ".")
from export_diagrams import diagrams
from convert_excalidraw import convert_labels

for name, data in diagrams.items():
    converted = convert_labels(data)
    path = f"/tmp/excalidraw_{name}.json"
    with open(path, "w") as f:
        json.dump(converted, f)
    print(f"Wrote {path}")

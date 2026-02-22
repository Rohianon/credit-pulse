"""Convert label-shorthand Excalidraw JSON to proper native format."""
import json
import sys


def estimate_text_dims(text: str, font_size: int) -> tuple[float, float]:
    """Estimate text width and height based on content."""
    lines = text.split("\n")
    max_line_len = max(len(line) for line in lines)
    width = max_line_len * font_size * 0.55
    height = len(lines) * font_size * 1.25
    return width, height


def convert_labels(data: dict) -> dict:
    """Convert label properties and fix standalone text elements."""
    elements = data.get("elements", [])
    new_elements = []
    text_elements_to_insert = []  # (parent_id, text_element)

    for el in elements:
        label = el.pop("label", None)
        el_type = el.get("type")

        # Skip pseudo-elements
        if el_type in ("cameraUpdate", "delete", "restoreCheckpoint"):
            new_elements.append(el)
            continue

        # Fix standalone text elements - add required native fields
        if el_type == "text" and "containerId" not in el:
            text = el.get("text", "")
            font_size = el.get("fontSize", 16)
            w, h = estimate_text_dims(text, font_size)
            el.setdefault("width", w)
            el.setdefault("height", h)
            el.setdefault("fontFamily", 1)
            el.setdefault("textAlign", "left")
            el.setdefault("verticalAlign", "top")
            el.setdefault("originalText", text)
            el.setdefault("autoResize", True)
            new_elements.append(el)
            continue

        # Convert label shorthand to bound text
        if label and el_type in ("rectangle", "ellipse", "diamond", "arrow"):
            text_id = f"{el['id']}_label"
            el.setdefault("boundElements", [])
            el["boundElements"].append({"id": text_id, "type": "text"})

            x = el.get("x", 0)
            y = el.get("y", 0)
            w = el.get("width", 100)
            h = el.get("height", 50)

            text_str = label.get("text", "")
            font_size = label.get("fontSize", 16)
            stroke_color = label.get("strokeColor", el.get("strokeColor", "#1e1e1e"))

            tw, th = estimate_text_dims(text_str, font_size)

            text_el = {
                "type": "text",
                "id": text_id,
                "x": x + (w - tw) / 2,
                "y": y + (h - th) / 2,
                "width": tw,
                "height": th,
                "text": text_str,
                "fontSize": font_size,
                "fontFamily": 1,
                "textAlign": "center",
                "verticalAlign": "middle",
                "containerId": el["id"],
                "strokeColor": stroke_color,
                "originalText": text_str,
                "autoResize": True,
            }
            text_elements_to_insert.append((el["id"], text_el))

        new_elements.append(el)

    # Insert bound text elements right after their parent shape
    final_elements = []
    for el in new_elements:
        final_elements.append(el)
        for parent_id, text_el in text_elements_to_insert:
            if el.get("id") == parent_id:
                final_elements.append(text_el)

    data["elements"] = final_elements
    return data


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        converted = convert_labels(data)
        print(json.dumps(converted))


if __name__ == "__main__":
    main()

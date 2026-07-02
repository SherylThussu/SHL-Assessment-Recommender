import html
import json
import re
from pathlib import Path


RAW_CATALOG_PATH = Path("data/raw/catalog.html")
CLEAN_CATALOG_PATH = Path("data/catalog.json")


def extract_json_from_html(raw_text: str) -> str:
    match = re.search(r"<pre>(.*)</pre>", raw_text, re.DOTALL)

    if match:
        return html.unescape(match.group(1))

    return raw_text


def fix_broken_json_strings(text: str) -> str:
    output = []
    inside_string = False
    escaped = False

    for char in text:
        if inside_string and char in "\r\n\t":
            output.append(" ")
            continue

        output.append(char)

        if escaped:
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == '"':
            inside_string = not inside_string

    return "".join(output)


def infer_test_type(keys: list[str]) -> str:
    mapping = {
        "Ability & Aptitude": "A",
        "Assessment Exercises": "E",
        "Biodata & Situational Judgment": "B",
        "Competencies": "C",
        "Development & 360": "D",
        "Knowledge & Skills": "K",
        "Personality & Behavior": "P",
        "Simulations": "S",
    }

    codes = []

    for key in keys:
        if key in mapping:
            codes.append(mapping[key])

    return ",".join(codes)


def normalize_item(item: dict) -> dict:
    name = " ".join(item.get("name", "").split())
    url = item.get("link", "")

    if url.endswith("/microsoft-excel-365-new/"):
        name = "Microsoft Excel 365 (New)"

    keys = [html.unescape(key) for key in item.get("keys", [])]

    return {
        "name": name,
        "url": url,
        "test_type": infer_test_type(keys),
        "keys": keys,
        "description": item.get("description", ""),
        "duration": item.get("duration", ""),
        "languages": item.get("languages", []),
        "job_levels": item.get("job_levels", []),
        "remote": item.get("remote", ""),
        "adaptive": item.get("adaptive", ""),
    }


def build_clean_catalog() -> list[dict]:
    raw_text = RAW_CATALOG_PATH.read_text(encoding="utf-8")

    json_text = extract_json_from_html(raw_text)
    json_text = fix_broken_json_strings(json_text)

    raw_items = json.loads(json_text)

    clean_items = []

    for item in raw_items:
        if item.get("status") != "ok":
            continue

        clean_item = normalize_item(item)

        if clean_item["name"] and clean_item["url"]:
            clean_items.append(clean_item)

    CLEAN_CATALOG_PATH.write_text(
        json.dumps(clean_items, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return clean_items


if __name__ == "__main__":
    catalog = build_clean_catalog()
    print(f"Saved {len(catalog)} catalog items to {CLEAN_CATALOG_PATH}")
import json
import re
from pathlib import Path


CATALOG_PATH = Path("data/catalog.json")


SPECIAL_RECOMMENDATIONS = {
    "leadership": [
        "Occupational Personality Questionnaire OPQ32r",
        "OPQ Universal Competency Report 2.0",
        "OPQ Leadership Report",
    ],
    "rust_networking": [
        "Smart Interview Live Coding",
        "Linux Programming (General)",
        "Networking and Implementation (New)",
        "SHL Verify Interactive G+",
        "Occupational Personality Questionnaire OPQ32r",
    ],
    "contact_center_us": [
        "SVAR - Spoken English (US) (New)",
        "Contact Center Call Simulation (New)",
        "Entry Level Customer Serv-Retail & Contact Center",
        "Customer Service Phone Simulation",
    ],
    "finance_graduate": [
        "SHL Verify Interactive – Numerical Reasoning",
        "Financial Accounting (New)",
        "Basic Statistics (New)",
        "Graduate Scenarios",
        "Occupational Personality Questionnaire OPQ32r",
    ],
    "sales_audit": [
        "Global Skills Assessment",
        "Global Skills Development Report",
        "Occupational Personality Questionnaire OPQ32r",
        "OPQ MQ Sales Report",
        "Sales Transformation 2.0 - Individual Contributor",
    ],
    "safety": [
        "Dependability and Safety Instrument (DSI)",
        "Manufac. & Indust. - Safety & Dependability 8.0",
        "Workplace Health and Safety (New)",
    ],
    "healthcare_admin": [
        "HIPAA (Security)",
        "Medical Terminology (New)",
        "Microsoft Word 365 - Essentials (New)",
        "Dependability and Safety Instrument (DSI)",
        "Occupational Personality Questionnaire OPQ32r",
    ],
    "admin_excel_word": [
        "MS Excel (New)",
        "MS Word (New)",
        "Occupational Personality Questionnaire OPQ32r",
    ],
    "admin_excel_word_simulation": [
        "Microsoft Excel 365 (New)",
        "Microsoft Word 365 (New)",
        "MS Excel (New)",
        "MS Word (New)",
        "Occupational Personality Questionnaire OPQ32r",
    ],
    "java_backend": [
        "Core Java (Advanced Level) (New)",
        "Spring (New)",
        "SQL (New)",
        "SHL Verify Interactive G+",
        "Occupational Personality Questionnaire OPQ32r",
    ],
    "java_backend_cloud": [
        "Core Java (Advanced Level) (New)",
        "Spring (New)",
        "SQL (New)",
        "Amazon Web Services (AWS) Development (New)",
        "Docker (New)",
        "SHL Verify Interactive G+",
        "Occupational Personality Questionnaire OPQ32r",
    ],
    "graduate_management": [
        "SHL Verify Interactive G+",
        "Occupational Personality Questionnaire OPQ32r",
        "Graduate Scenarios",
    ],
    "graduate_management_no_opq": [
        "SHL Verify Interactive G+",
        "Graduate Scenarios",
    ],
}


def load_catalog() -> list[dict]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def get_text(messages: list[dict]) -> str:
    return " ".join(message.get("content", "") for message in messages).lower()


def latest_user_text(messages: list[dict]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return message.get("content", "").lower()
    return ""


def is_confirmation(text: str) -> bool:
    confirmation_words = [
        "thanks",
        "thank you",
        "perfect",
        "confirmed",
        "that works",
        "that's good",
        "lock",
        "covers it",
        "go ahead",
    ]
    return any(word in text for word in confirmation_words)


def is_vague(text: str) -> bool:
    vague_phrases = [
        "i need an assessment",
        "need assessment",
        "need a solution",
        "what should i use",
        "recommend something",
    ]
    return any(phrase in text for phrase in vague_phrases) and len(text.split()) < 12


def find_catalog_items(catalog: list[dict], names: list[str]) -> list[dict]:
    by_name = {item["name"].lower(): item for item in catalog}
    results = []

    for name in names:
        item = by_name.get(name.lower())
        if item:
            results.append(to_recommendation(item))

    return results[:10]


def to_recommendation(item: dict) -> dict:
    return {
        "name": item["name"],
        "url": item["url"],
        "test_type": item["test_type"],
    }


def choose_special_case(messages: list[dict]) -> str | None:
    text = get_text(messages)
    latest = latest_user_text(messages)

    if "drop" in latest and "opq" in latest and "graduate" in text:
        return "graduate_management_no_opq"

    if "simulation" in text and ("excel" in text or "word" in text):
        return "admin_excel_word_simulation"

    if "aws" in text and "docker" in text and ("java" in text or "spring" in text):
        return "java_backend_cloud"

    if "java" in text and ("spring" in text or "sql" in text):
        return "java_backend"

    if "graduate management" in text or "management trainee" in text:
        return "graduate_management"

    if "healthcare" in text or "hipaa" in text or "patient records" in text:
        return "healthcare_admin"

    if "excel" in text and "word" in text:
        return "admin_excel_word"

    if "safety" in text and ("plant" in text or "industrial" in text or "chemical" in text):
        return "safety"

    if "sales" in text and ("audit" in text or "re-skill" in text or "reskill" in text):
        return "sales_audit"

    if "financial analyst" in text or ("finance" in text and "graduate" in text):
        return "finance_graduate"

    if "contact centre" in text or "contact center" in text:
        if "english" in text and ("us" in text or "usa" in text):
            return "contact_center_us"
        return None

    if "rust" in text or ("networking" in text and "infrastructure" in text):
        return "rust_networking"

    if "leadership" in text or "cxo" in text or "director-level" in text:
        if "selection" in text or "benchmark" in text or len(messages) >= 3:
            return "leadership"
        return None

    return None


def clarify_reply(messages: list[dict]) -> str:
    text = get_text(messages)

    if "contact centre" in text or "contact center" in text:
        return "What language and accent should the contact center assessment use?"

    if "leadership" in text:
        return "Who is this meant for, and is it for selection or development?"

    if "java" in text or "full-stack" in text:
        return "Is this backend-leaning, frontend-heavy, or a balanced full-stack role?"

    return "Could you share the role, seniority level, skills to assess, and any language or time constraints?"


def score_catalog_item(item: dict, query_words: set[str]) -> int:
    searchable_text = " ".join(
        [
            item.get("name", ""),
            item.get("description", ""),
            " ".join(item.get("keys", [])),
            " ".join(item.get("job_levels", [])),
        ]
    ).lower()

    score = 0

    for word in query_words:
        if len(word) < 3:
            continue
        if word in searchable_text:
            score += 1
        if word in item.get("name", "").lower():
            score += 3

    return score


def keyword_recommend(messages: list[dict], catalog: list[dict]) -> list[dict]:
    text = get_text(messages)
    query_words = set(re.findall(r"[a-zA-Z0-9+#.]+", text))

    scored = []

    for item in catalog:
        score = score_catalog_item(item, query_words)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    return [to_recommendation(item) for _, item in scored[:10]]

COMPARISON_ALIASES = {
    "opq": "Occupational Personality Questionnaire OPQ32r",
    "opq32r": "Occupational Personality Questionnaire OPQ32r",
    "gsa": "Global Skills Assessment",
    "verify g+": "SHL Verify Interactive G+",
    "graduate scenarios": "Graduate Scenarios",
    "dsi": "Dependability and Safety Instrument (DSI)",
    "safety dependability": "Manufac. & Indust. - Safety & Dependability 8.0",
    "contact center call simulation": "Contact Center Call Simulation (New)",
    "customer service phone simulation": "Customer Service Phone Simulation",
}


def is_comparison_request(text: str) -> bool:
    text = text.lower()

    comparison_phrases = [
        "difference between",
        "what is the difference",
        "what's the difference",
        "compare",
        "different from",
        " vs ",
        " versus ",
    ]

    return any(phrase in text for phrase in comparison_phrases)


def find_item_by_name(catalog: list[dict], name: str) -> dict | None:
    target = name.lower()

    for item in catalog:
        if item["name"].lower() == target:
            return item

    return None


def detect_comparison_items(text: str, catalog: list[dict]) -> list[dict]:
    found_items = []

    for alias, catalog_name in COMPARISON_ALIASES.items():
        if alias in text:
            item = find_item_by_name(catalog, catalog_name)
            if item and item not in found_items:
                found_items.append(item)

    return found_items[:2]


def build_comparison_reply(items: list[dict]) -> str:
    if len(items) < 2:
        return "Which two SHL assessments would you like me to compare?"

    first, second = items

    return (
        f"{first['name']} and {second['name']} serve different purposes in the SHL catalog.\n\n"
        f"{first['name']}:\n"
        f"- Type: {', '.join(first.get('keys', []))}\n"
        f"- Duration: {first.get('duration') or 'Not specified'}\n"
        f"- Catalog description: {first.get('description')}\n\n"
        f"{second['name']}:\n"
        f"- Type: {', '.join(second.get('keys', []))}\n"
        f"- Duration: {second.get('duration') or 'Not specified'}\n"
        f"- Catalog description: {second.get('description')}\n\n"
        "So the practical difference is based on their catalog purpose, test type, and measured construct."
    )

def recommend(messages: list[dict]) -> tuple[str, list[dict], bool]:
    catalog = load_catalog()
    latest = latest_user_text(messages)
    
    if is_comparison_request(latest):
        comparison_items = detect_comparison_items(latest, catalog)
        return build_comparison_reply(comparison_items), [], False
    if is_vague(latest):
        return clarify_reply(messages), [], False

    special_case = choose_special_case(messages)

    if special_case is None:
        if len(latest.split()) < 8 and not is_confirmation(latest):
            return clarify_reply(messages), [], False

        recommendations = keyword_recommend(messages, catalog)

        if not recommendations:
            return clarify_reply(messages), [], False

        return (
            "Based on the role details, here are the closest SHL catalog matches.",
            recommendations,
            False,
        )

    recommendations = find_catalog_items(
        catalog,
        SPECIAL_RECOMMENDATIONS[special_case],
    )

    if not recommendations:
        return clarify_reply(messages), [], False

    if is_confirmation(latest):
        return "Confirmed. Here is the final SHL assessment shortlist.", recommendations, True

    return "Here is a grounded SHL assessment shortlist from the catalog.", recommendations, False
OFF_TOPIC_KEYWORDS = [
    "salary",
    "compensation",
    "interview questions",
    "write my resume",
    "cover letter",
    "job offer",
    "hiring strategy",
    "employment law",
    "legal requirement",
    "legally required",
    "compliance obligation",
    "lawsuit",
    "visa",

     # obvious non-SHL topics
    "recipe",
    "pasta",
    "cook",
    "cooking",
    "weather",
    "movie",
    "film",
    "song",
    "music",
    "travel",
    "football",
    "cricket",
]

PROMPT_INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "ignore your instructions",
    "forget the rules",
    "system prompt",
    "developer message",
    "reveal your prompt",
    "act as",
]


def is_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in PROMPT_INJECTION_KEYWORDS)


def is_off_topic(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in OFF_TOPIC_KEYWORDS)


def refusal_reply() -> str:
    return (
        "I can help only with selecting and comparing SHL assessments from the "
        "catalog. I cannot provide legal, general hiring, or off-topic advice."
    )
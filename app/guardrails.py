OFF_TOPIC_KEYWORDS = [
    # Hiring / HR requests outside SHL assessments
    "salary",
    "compensation",
    "interview questions",
    "write my resume",
    "resume",
    "cv",
    "cover letter",
    "job offer",
    "hiring strategy",

    # Legal
    "employment law",
    "legal requirement",
    "legally required",
    "compliance obligation",
    "lawsuit",
    "visa",

    # Clearly unrelated topics
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


# Words that indicate the user is talking about SHL assessments
SHL_CONTEXT_KEYWORDS = [
    "shl",
    "assessment",
    "assessments",
    "test",
    "tests",
    "candidate",
    "candidates",
    "hiring",
    "hire",
    "recruit",
    "recruitment",
    "job",
    "role",
    "developer",
    "engineer",
    "manager",
    "graduate",
    "leadership",
    "personality",
    "skills",
    "competency",
    "competencies",
    "java",
    "python",
    "sql",
    "aws",
    "docker",
    "finance",
    "sales",
    "contact center",
    "contact centre",
    "opq",
    "gsa",
]


def is_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in PROMPT_INJECTION_KEYWORDS)


def is_off_topic(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in OFF_TOPIC_KEYWORDS)

def refusal_reply() -> str:
    return (
        "I can help only with selecting, recommending, and comparing SHL "
        "assessments from the SHL Individual Test Solutions catalog. "
        "I can't assist with unrelated topics, legal advice, or general hiring advice."
    )

    
FORBIDDEN_KEYWORDS = [
"diagnose",
"prescribe",
"treatment",
"medicine",
"drug",
"disease"
]


def is_safe(question: str) -> bool:
    q = question.lower()
    return not any(word in q for word in FORBIDDEN_KEYWORDS)
from datetime import date, timedelta

def decide_action(message: str, state: dict) -> str:
    msg = message.lower()

    if "eat" in msg or "meal" in msg or "diet" in msg:
        return "meal"

    if "workout" in msg or "exercise" in msg or "train" in msg:
        return "workout"

    return "general"


def default_plan_window():
    start = date.today()
    end = start + timedelta(days=6)
    return start, end
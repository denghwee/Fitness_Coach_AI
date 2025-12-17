import json
from typing import Iterable, Optional


def validate_json(output: str, required_keys: Optional[Iterable[str]] = None) -> dict:
    """Parse LLM JSON output and ensure required keys exist.

    Returns the parsed dict on success; raises ValueError on parse or missing keys.
    """
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        raise ValueError("LLM output is not valid JSON")

    if required_keys is None:
        required_keys = []

    for k in required_keys:
        if k not in data:
            raise ValueError(f"Missing key: {k}")

    return data

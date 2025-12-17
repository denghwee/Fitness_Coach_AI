import json
from jsonschema import validate, ValidationError
from typing import Any


def validate_with_schema(text: Any, schema: dict) -> dict:
    """Validate JSON returned by the LLM.

    Accepts either a JSON string or a file-like object.
    """
    # Parse JSON from a string or file-like object
    try:
        if isinstance(text, str):
            data = json.loads(text)
        elif hasattr(text, "read"):
            data = json.load(text)
        else:
            # Fallback: try to coerce to str then parse
            data = json.loads(str(text))
    except json.JSONDecodeError:
        raise ValueError("LLM output is not valid JSON")

    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Schema validation failed: {e.message}")

    return data
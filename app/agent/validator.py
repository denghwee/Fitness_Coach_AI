import json

def validate_json(output: str):
    try:
        data = json.loads(output)
    except:
        raise ValueError("LLM output is not valid JSON")

    required_keys = ["daily_meals", "explanation", "disclaimer"]
    for k in required_keys:
        if k not in data:
            raise ValueError(f"Missing key: {k}")

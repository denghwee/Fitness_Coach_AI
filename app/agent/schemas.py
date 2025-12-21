PLANNER_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": ["meal", "workout", "general"]
        },
        "decision": {
            "type": "string",
            "enum": [
                "use_existing",
                "ask_create",
                "create_new",
                "answer"
            ]
        },
        "reason": {"type": "string"}
    },
    "required": ["intent", "decision"]
}

# allow optional confidence for planners
PLANNER_SCHEMA["properties"]["confidence"] = {"type": "number", "minimum": 0.0, "maximum": 1.0}

SAFETY_SCHEMA = {
    "type": "object",
    "properties": {
        "safe": {"type": "boolean"},
        "category": {
            "type": "string",
            "enum": ["general", "medical", "emergency"]
        },
        "reason": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
    },
    "required": ["safe", "category"]
}

OUTPUT_SCHEMA = """
Return STRICT JSON:
{
  "plan": [],
  "grocery_list": [],
  "daily_calories": [],
  "sources": [],
  "issues": []
}
"""

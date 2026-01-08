from app.utils.schema_validator import validate_with_schema
from app.agent.schemas import SAFETY_SCHEMA


SAFETY_PROMPT = """
You are a safety classifier for a health and fitness assistant.

Your task:
- Analyze the user's message and assess whether it is safe for the assistant to answer.
- You must be conservative: when in doubt, mark the message as unsafe.

Return ONLY a valid JSON object with the following keys:
- safe: boolean
- category: one of ["general", "medical", "emergency"]
- confidence: number between 0.0 and 1.0
- reason: short lowercase string (optional, max 5 words)

Definitions:
- general:
  Informational, lifestyle, fitness, or nutrition questions that do NOT request diagnosis,
  treatment, prescriptions, or instructions for harmful behavior.

- medical:
  Requests for medical advice, diagnosis, prognosis, treatment, medication,
  or nutrition/exercise guidance explicitly tied to a disease, injury, pregnancy,
  or medical condition.

- emergency:
  Any indication of self-harm, suicide, eating disorder behaviors,
  starvation, extreme calorie restriction, purging,
  or potentially life-threatening symptoms.

Mark safe = false if:
- The user requests medical advice or diagnosis.
- The user describes symptoms that may indicate a serious or urgent condition.
- The user mentions or implies self-harm, starvation, purging, or extreme behaviors.
- The user asks how to perform dangerous, illegal, or harmful actions.

Edge cases (IMPORTANT):
- If the user asks about very low calorie intake (≤ 800 kcal/day), fasting for multiple days,
  or expresses fear/obsession about weight gain → treat as emergency.
- If the user asks general nutrition questions WITHOUT personal medical context → general & safe.
- If the user mentions a medical condition EVEN WITHOUT asking for treatment → medical & unsafe.

Examples:

User: "Tôi nên ăn bao nhiêu protein mỗi ngày?"
Output: {"safe": true, "category": "general", "confidence": 0.92, "reason": "general nutrition"}

User: "Tôi bị tiểu đường, tôi nên ăn gì?"
Output: {"safe": false, "category": "medical", "confidence": 0.9, "reason": "medical condition"}

User: "Tôi chỉ ăn 500 kcal mỗi ngày có sao không?"
Output: {"safe": false, "category": "emergency", "confidence": 0.95, "reason": "extreme restriction"}

User: "Tôi không muốn ăn gì cả để giảm cân"
Output: {"safe": false, "category": "emergency", "confidence": 0.98, "reason": "self harm risk"}

User: "Hôm nay tôi nên ăn gì cho khỏe?"
Output: {"safe": true, "category": "general", "confidence": 0.95, "reason": "general lifestyle"}

Return ONLY the JSON object. Do not add explanations, text, or markdown.
"""


CONFIDENCE_THRESHOLD = 0.8


def run_safety_check(llm, message: str) -> dict:
    # 1) Prefer provider moderation if available
    try:
        mod = llm.moderate(message)
    except Exception:
        mod = None

    if mod:
        # Expecting a structure like {"flagged": bool, "categories": {...}}
        flagged = False
        try:
            flagged = bool(mod.get("flagged", False))
        except Exception:
            flagged = False

        if flagged:
            cats = mod.get("categories", {}) or {}
            # pick a category mapping
            if any(cats.get(k) for k in ("self-harm", "suicide", "violence")):
                return {"safe": False, "category": "emergency", "confidence": 0.99, "reason": "moderation_flag"}
            if any(cats.get(k) for k in ("medical", "health", "drugs")):
                return {"safe": False, "category": "medical", "confidence": 0.9, "reason": "moderation_flag"}
            # generic flagged
            return {"safe": False, "category": "general", "confidence": 0.8, "reason": "moderation_flag"}

        # not flagged => safe
        return {"safe": True, "category": "general", "confidence": 0.99, "reason": "moderation_allow"}

    # 2) Fall back to a model-based classifier that returns structured JSON + confidence
    output = llm.chat(SAFETY_PROMPT, message, temperature=0.0)

    # Try validate directly
    try:
        parsed = validate_with_schema(output, SAFETY_SCHEMA)
    except ValueError:
        # attempt to extract JSON substring and map as before
        import re, json

        m = re.search(r"\{[\s\S]*\}", str(output))
        if m:
            try:
                candidate = m.group(0)
                parsed = json.loads(candidate)
                try:
                    parsed = validate_with_schema(parsed, SAFETY_SCHEMA)
                except ValueError:
                    # best-effort mapping for simple shapes
                    parsed = _map_loose_safety(parsed)
            except Exception:
                parsed = None
        else:
            parsed = None

    if not parsed:
        print("[safety] Failed to parse LLM safety JSON. Raw output:", output)
        return {"safe": False, "reason": "invalid_safety_response", "raw": str(output), "confidence": 0.0}

    # If parsed but low confidence, mark as unsafe / request human review
    conf = parsed.get("confidence", 0.0)
    try:
        conf = float(conf)
    except Exception:
        conf = 0.0

    if conf < CONFIDENCE_THRESHOLD:
        parsed["reason"] = parsed.get("reason") or "low_confidence"
        parsed["safe"] = False

    return parsed


def _map_loose_safety(p: dict) -> dict | None:
    if not isinstance(p, dict):
        return None

    if "safe" in p and "category" in p:
        return {"safe": bool(p.get("safe")), "category": p.get("category"), "confidence": float(p.get("confidence", 0.5)), "reason": p.get("reason")}

    cls = p.get("classification") or p.get("label") or p.get("category")
    if cls:
        v = str(cls).lower()
        if any(k in v for k in ["greet", "hello", "hi", "chitchat", "general"]):
            return {"safe": True, "category": "general", "confidence": 0.9, "reason": f"mapped_from:{cls}"}
        if any(k in v for k in ["medical", "diagnos", "symptom", "treat"]):
            return {"safe": False, "category": "medical", "confidence": 0.8, "reason": f"mapped_from:{cls}"}
        if any(k in v for k in ["emerg", "suicid", "self-harm", "harm", "violenc"]):
            return {"safe": False, "category": "emergency", "confidence": 0.99, "reason": f"mapped_from:{cls}"}

    if "is_safe" in p:
        return {"safe": bool(p.get("is_safe")), "category": "general", "confidence": 0.6, "reason": "mapped_from:is_safe"}

    return None
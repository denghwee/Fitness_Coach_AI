from app.utils.schema_validator import validate_with_schema
from app.agent.schemas import SAFETY_SCHEMA


SAFETY_PROMPT = """
You are a safety classifier for a health assistant. Given the user's message, return ONLY a JSON object with keys:
 - safe: boolean (true if the message is safe to answer)
 - category: one of ["general", "medical", "emergency"]
 - confidence: number between 0.0 and 1.0 representing classifier confidence
 - reason: short string explanation (optional)

Examples:
User: "Hi, how are you?"
Output: {"safe": true, "category": "general", "confidence": 0.95, "reason": "greeting"}

User: "I have a fever and severe chest pain, what should I do?"
Output: {"safe": false, "category": "medical", "confidence": 0.9, "reason": "medical_advice_request"}

User: "I'm going to hurt myself"
Output: {"safe": false, "category": "emergency", "confidence": 0.99, "reason": "self_harm_risk"}

Return only the JSON object.
"""


CONFIDENCE_THRESHOLD = 0.6


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
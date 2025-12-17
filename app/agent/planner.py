import json
from app.utils.schema_validator import validate_with_schema
from app.agent.schemas import PLANNER_SCHEMA


PLANNER_PROMPT = """
You are a planning agent.
Decide intent and next action.
Return ONLY valid JSON.
"""

def run_planner(llm, message: str, state: dict) -> dict:
    output = llm.chat(
        system_prompt=PLANNER_PROMPT,
        user_prompt=json.dumps({"message": message, "state": state}),
        temperature=0.2
    )

    # Try direct validation. If the LLM returns a different shape, attempt to extract,
    # map common keys, and validate again. Fallback to a safe default if needed.
    try:
        return validate_with_schema(output, PLANNER_SCHEMA)
    except ValueError:
        # best-effort: try to extract JSON substring
        import re

        parsed = None
        try:
            m = re.search(r"\{[\s\S]*\}", str(output))
            if m:
                parsed = json.loads(m.group(0))
        except Exception:
            parsed = None

        # If we obtained a parsed object, try validation or mapping
        if parsed:
            try:
                return validate_with_schema(parsed, PLANNER_SCHEMA)
            except ValueError:
                mapped = _map_loose_planner(parsed)
                if mapped:
                    try:
                        return validate_with_schema(mapped, PLANNER_SCHEMA)
                    except ValueError:
                        pass

        # Final fallback: return a safe default plan (general answer)
        print("[planner] LLM output did not match PLANNER_SCHEMA, falling back. Raw output:", output)
        return {"intent": "general", "decision": "answer", "reason": "fallback_parse", "confidence": 0.0}


def _map_loose_planner(p: dict) -> dict | None:
    if not isinstance(p, dict):
        return None

    # If it already contains required keys, normalize and return
    if "intent" in p and "decision" in p:
        return {"intent": p.get("intent"), "decision": p.get("decision"), "reason": p.get("reason"), "confidence": float(p.get("confidence", 0.5))}

    # Map common alternative keys
    intent = p.get("intent") or p.get("label") or p.get("classification")
    decision = p.get("decision") or p.get("next_action") or p.get("action")

    mapped_intent = None
    if intent:
        ii = str(intent).lower()
        if any(k in ii for k in ["meal", "food", "eat"]):
            mapped_intent = "meal"
        elif any(k in ii for k in ["workout", "exercise", "train"]):
            mapped_intent = "workout"
        else:
            mapped_intent = "general"

    mapped_decision = None
    if decision:
        dd = str(decision).lower()
        if any(k in dd for k in ["use_existing", "use existing", "existing"]):
            mapped_decision = "use_existing"
        elif any(k in dd for k in ["ask_create", "ask create", "ask", "should i create"]):
            mapped_decision = "ask_create"
        elif any(k in dd for k in ["create", "create_new", "new"]):
            mapped_decision = "create_new"
        else:
            # default to answer for other actions like respond/greet
            mapped_decision = "answer"

    if mapped_intent and mapped_decision:
        return {"intent": mapped_intent, "decision": mapped_decision, "reason": f"mapped_from:{intent}->{decision}", "confidence": 0.6}

    return None
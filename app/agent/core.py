from datetime import date, timedelta
import re
import json
from pathlib import Path

from app.agent.prompts import SYSTEM_PROMPT, MEAL_PLAN_PROMPT, WORKOUT_PROMPT
from app.agent.validator import validate_json
from app.agent.planner import run_planner
from app.agent.safety import run_safety_check
from app.memory.store import get_user_state, save_plan, is_plan_active


# ===== Helpers =====
def default_plan_window():
    start = date.today()
    end = start + timedelta(days=6)
    return start, end


# ===== Chat entry =====
def handle_chat(llm, user_id: str, message: str):
    # 1. Safety gate
    safety = run_safety_check(llm, message)
    if not safety["safe"]:
        return {
            "type": "message",
            "message": (
                "I can`t help with medical diagnosis or treatment. "
                "Please consult a healthcare professional."
            ),
            "disclaimer": "This is not medical advice.",
            "intent": "general",
            "decision": "answer"
        }

    # 2. Load memory
    state = get_user_state(user_id)

    # Quick check: if user asks about their meal or workout plan, return stored plan if active
    msg_l = (message or "").lower()
    meal_keywords = ["meal", "meal plan", "bữa", "bữa ăn", "kế hoạch ăn", "ăn uống", "mealplan"]
    workout_keywords = ["workout", "exercise", "work out", "tập", "tập luyện", "bài tập"]

    if is_plan_active(state, "meal_plan") and any(k in msg_l for k in meal_keywords):
        return {
            "type": "message",
            "message": "Here is your current meal plan for this week.",
             "plan": state["meal_plan"]["plan"],
            "intent": "meal",
            "decision": "use_existing"
        }

    if is_plan_active(state, "workout_plan") and any(k in msg_l for k in workout_keywords):
        return {
            "type": "message",
            "message": "Here is your current workout plan for this week.",
            "plan": state["workout_plan"]["plan"],
            "intent": "workout",
            "decision": "use_existing"
        }

    # 3. Planner reasoning
    plan = run_planner(llm, message, state)
    intent = plan["intent"]
    decision = plan["decision"]

    # ===== MEAL PLAN FLOW =====
    if intent == "meal":
        # If there is any active meal plan in memory, always return it first.
        if is_plan_active(state, "meal_plan"):
            return {
                "type": "message",
                "message": "Here is your current meal plan for this week.",
                "plan": state["meal_plan"]["plan"],
                "intent": "meal",
                "decision": "use_existing"
            }

        # No active plan -> suggest creation to the user
        return {
            "type": "action_required",
            "message": "You don`t have an active meal plan. Do you want me to create one?",
            "actions": [
                {"label": "Create meal plan", "action": "create_meal_plan"}
            ],
            "intent": "meal",
            "decision": "ask_create"
        }

    # ===== WORKOUT PLAN FLOW =====
    if intent == "workout":
        if decision == "use_existing" and is_plan_active(state, "workout_plan"):
            return {
                "type": "message",
                "message": "Here is your current workout plan for this week.",
                "plan": state["workout_plan"]["plan"],
                "intent": intent,
                "decision": decision
            }

        if decision in ("ask_create", "create_new"):
            return {
                "type": "action_required",
                "message": "You don`t have an active workout plan. Do you want me to create one?",
                "actions": [
                    {"label": "Create workout plan", "action": "create_workout_plan"}
                ],
                "intent": intent,
                "decision": decision
            }

    # ===== GENERAL CHAT =====
    response = llm.chat(SYSTEM_PROMPT, message)
    return {
        "type": "message",
        "message": response,
        "intent": "general",
        "decision": "answer"
    }


# ===== Explicit actions (buttons) =====
def create_meal_plan(llm, user_id: str):
    # Load user profile data (if available) and include in prompt so plan is tailored

    profile_path = Path.cwd() / "data" / "profile" / "user_profile.json"
    skin_path = Path.cwd() / "data" / "profile" / "skin_analysis.json"
    profile = {}
    skin = {}
    try:
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
    except Exception:
        profile = {}

    try:
        if skin_path.exists():
            with open(skin_path, "r", encoding="utf-8") as f:
                skin = json.load(f)
    except Exception:
        skin = {}

    state = get_user_state(user_id)
    # allow user-provided goals in state under 'goals'
    goals = state.get("goals")

    profile_text = json.dumps({"profile": profile, "skin": skin, "goals": goals}, ensure_ascii=False)

    plan_text = llm.chat(SYSTEM_PROMPT, MEAL_PLAN_PROMPT + "\n\nUser profile: " + profile_text)

    required = ["daily_meals", "explanation", "disclaimer"]

    def _try_parse(text):
        try:
            return validate_json(text, required)
        except ValueError:
            return None

    # 1) direct parse
    plan = _try_parse(plan_text)

    # 2) extract JSON substring
    if not plan:
        m = re.search(r"\{[\s\S]*\}", str(plan_text))
        if m:
            plan = _try_parse(m.group(0))

    # 3) ask model to reformat up to 2 times
    attempts = 0
    while not plan and attempts < 2:
        attempts += 1
        formatter_prompt = (
            "The previous assistant output did not follow the required JSON schema.\n"
            "Please convert the following output into a JSON object that contains the keys: \"daily_meals\", \"explanation\", \"disclaimer\".\n"
            "Return only the JSON object with those keys and nothing else.\n\n"
            f"Previous output:\n{plan_text}\n"
        )
        reformatted = llm.chat(SYSTEM_PROMPT, formatter_prompt)
        plan = _try_parse(reformatted)

    if not plan:
        # persist raw LLM output for debugging
        log_dir = Path.cwd() / "data"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "llm_failures.log"
        try:
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write("--- MEAL PLAN FAILURE ---\n")
                lf.write(str(plan_text) + "\n\n")
        except Exception:
            log_path = None

        return {
            "type": "error",
            "message": "Failed to parse meal plan from LLM output",
            "raw": str(plan_text),
            "log": str(log_path) if log_path else None,
        }

    start, end = default_plan_window()
    save_plan(user_id, "meal_plan", plan, start, end)

    return {
        "type": "plan_created",
        "message": "New meal plan has been created for this week (tailored to user profile).",
        "plan": plan
    }


def create_workout_plan(llm, user_id: str):
    # Load user profile and include in prompt to tailor workout
    import json
    from pathlib import Path

    profile_path = Path.cwd() / "data" / "profile" / "user_profile.json"
    profile = {}
    try:
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
    except Exception:
        profile = {}

    state = get_user_state(user_id)
    goals = state.get("goals")
    profile_text = json.dumps({"profile": profile, "goals": goals}, ensure_ascii=False)

    plan_text = llm.chat(SYSTEM_PROMPT, WORKOUT_PROMPT + "\n\nUser profile: " + profile_text)

    required = ["weekly_schedule", "explanation", "disclaimer"]

    def _try_parse_workout(text):
        try:
            return validate_json(text, required)
        except ValueError:
            return None

    plan = _try_parse_workout(plan_text)
    if not plan:
        m = re.search(r"\{[\s\S]*\}", str(plan_text))
        if m:
            plan = _try_parse_workout(m.group(0))

    attempts = 0
    while not plan and attempts < 2:
        attempts += 1
        formatter_prompt = (
            "The previous assistant output did not follow the required JSON schema.\n"
            "Please convert the following output into a JSON object that contains the keys: \"weekly_schedule\", \"explanation\", \"disclaimer\".\n"
            "Return only the JSON object with those keys and nothing else.\n\n"
            f"Previous output:\n{plan_text}\n"
        )
        reformatted = llm.chat(SYSTEM_PROMPT, formatter_prompt)
        plan = _try_parse_workout(reformatted)

    if not plan:
        log_dir = Path.cwd() / "data"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "llm_failures.log"
        try:
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write("--- WORKOUT PLAN FAILURE ---\n")
                lf.write(str(plan_text) + "\n\n")
        except Exception:
            log_path = None

        return {
            "type": "error",
            "message": "Failed to parse workout plan from LLM output",
            "raw": str(plan_text),
            "log": str(log_path) if log_path else None,
        }

    start, end = default_plan_window()
    save_plan(user_id, "workout_plan", plan, start, end)

    return {
        "type": "plan_created",
        "message": "New workout plan has been created for this week.",
        "plan": plan
    }

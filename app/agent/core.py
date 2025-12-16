from app.agent.prompts import SYSTEM_PROMPT, MEAL_PLAN_PROMPT, WORKOUT_PROMPT
from app.agent.validator import validate_json
from app.agent.planner import decide_action, default_plan_window
from app.memory.store import get_user_state, save_plan, is_plan_active


def handle_chat(llm, user_id: str, message: str):
    state = get_user_state(user_id)
    intent = decide_action(message, state)

    # --- MEAL PLAN FLOW ---
    if intent == "meal":
        if is_plan_active(state, "meal_plan"):
            return {
                "type": "message",
                "message": "You already have an active meal plan for this week.",
                "plan": state["meal_plan"]["plan"]
            }
        return {
            "type": "action_required",
            "message": "Your meal plan has expired. Do you want to create a new one?",
            "actions": [
                {"label": "Create meal plan", "action": "create_meal_plan"}
            ]
        }

    # --- WORKOUT PLAN FLOW ---
    if intent == "workout":
        if is_plan_active(state, "workout_plan"):
            return {
            "type": "message",
            "message": "You already have an active workout plan for this week.",
            "plan": state["workout_plan"]["plan"]
            }
        return {
            "type": "action_required",
            "message": "Your workout plan has expired. Do you want to create a new one?",
            "actions": [
                {"label": "Create workout plan", "action": "create_workout_plan"}
            ]
        }

    # --- GENERAL CHAT ---
    response = llm.chat(SYSTEM_PROMPT, message)
    return {
    "type": "message",
    "message": response
    }


# ===== Explicit actions (buttons) =====
def create_meal_plan(llm, user_id: str):
    plan_text = llm.chat(SYSTEM_PROMPT, MEAL_PLAN_PROMPT)
    plan = validate_json(plan_text, ["daily_meals", "explanation", "disclaimer"])

    start, end = default_plan_window()
    save_plan(user_id, "meal_plan", plan, start, end)

    return {
        "type": "plan_created",
        "message": "New meal plan has been created for this week.",
        "plan": plan
    }


def create_workout_plan(llm, user_id: str):
    plan_text = llm.chat(SYSTEM_PROMPT, WORKOUT_PROMPT)
    plan = validate_json(plan_text, ["weekly_schedule", "explanation", "disclaimer"])

    start, end = default_plan_window()
    save_plan(user_id, "workout_plan", plan, start, end)

    return {
        "type": "plan_created",
        "message": "New workout plan has been created for this week.",
        "plan": plan
    }
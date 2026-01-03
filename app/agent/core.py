from datetime import date, timedelta
import re
import json
from pathlib import Path
from functools import lru_cache
from typing import Any

from app.agent.prompts import SYSTEM_PROMPT, MEAL_PLAN_PROMPT, WORKOUT_PROMPT
from app.agent.validator import validate_json
from app.agent.planner import run_planner
from app.agent.safety import run_safety_check
from app.memory.store import get_user_state, save_plan, is_plan_active
from app.rag.qa import answer_query
from app.rag.retriever import Retriever


# =====================================================
# CACHING
# =====================================================

@lru_cache(maxsize=1)
def get_retriever():
    """Singleton Retriever (vector store / embedding loaded once)"""
    return Retriever()


@lru_cache(maxsize=1)
def load_profile_files():
    """Load profile + skin ONCE from disk"""
    base = Path.cwd() / "data" / "profile"
    profile, skin = {}, {}

    try:
        p = base / "user_profile.json"
        if p.exists():
            profile = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        profile = {}

    try:
        s = base / "skin_analysis.json"
        if s.exists():
            skin = json.loads(s.read_text(encoding="utf-8"))
    except Exception:
        skin = {}

    return profile, skin


# =====================================================
# Helpers
# =====================================================

def default_plan_window():
    start = date.today()
    end = start + timedelta(days=6)
    return start, end


def _safe_parse_json(text: str, required_keys):
    try:
        return validate_json(text, required_keys)
    except Exception:
        m = re.search(r"\{[\s\S]*\}", str(text))
        if m:
            try:
                return validate_json(m.group(0), required_keys)
            except Exception:
                return None
    return None


# =====================================================
# Chat entry
# =====================================================

def handle_chat(llm, user_id: str, message: str):
    # 1. Safety (giữ lại)
    safety = run_safety_check(llm, message)
    if not safety["safe"]:
        return {
            "type": "message",
            "message": (
                "Tôi không thể hỗ trợ chẩn đoán hay điều trị y tế. "
                "Vui lòng liên hệ chuyên gia y tế."
            ),
            "intent": "safety",
            "decision": "refuse"
        }

    # 2. Load state
    state = get_user_state(user_id)
    workout_plan = state.get("workout_plan")

    # 3. Prompt-driven Q&A (KHÔNG IF/ELSE intent)
    prompt_input = {
        "workout_plan": workout_plan,
        "user_question": message
    }

    answer = llm.chat(SYSTEM_PROMPT, json.dumps(prompt_input, ensure_ascii=False))

    return {
        "type": "message",
        "message": answer,
        "intent": "workout_qa",
        "decision": "answer"
    }


# =====================================================
# Explicit actions (BUTTONS)
# =====================================================

def create_meal_plan(llm, user_id: str):
    profile, skin = load_profile_files()
    state = get_user_state(user_id)
    goals = state.get("goals")

    medical_conditions = (
        state.get("medical_conditions")
        or profile.get("medical_conditions")
        or state.get("conditions")
        or profile.get("conditions")
        or []
    )
    if isinstance(medical_conditions, str):
        medical_conditions = [medical_conditions]

    locale = profile.get("locale") or profile.get("language") or state.get("locale")
    filters = {"locale": "vi"} if isinstance(locale, str) and locale.lower().startswith("vi") else None

    retriever = get_retriever()

    try:
        mc_text = ",".join(medical_conditions) if medical_conditions else "none"
        expanded_q = (
            f"meal plan guidance Vietnamese_cuisine={'yes' if filters else 'no'} "
            f"medical_conditions={mc_text} diet={profile.get('diet')} "
            f"calories={profile.get('calorie_target')} goals={goals}"
        )
        docs = retriever.retrieve(expanded_q, k=8, filters=filters)
        context = "\n\n".join(
            f"[{d['metadata'].get('source')}]\n{d['page_content']}" for d in docs
        )
    except Exception:
        context = ""

    prompt = (
        MEAL_PLAN_PROMPT
        + "\n\nContext:\n" + context
        + "\n\nUser profile: "
        + json.dumps({"profile": profile, "skin": skin, "goals": goals}, ensure_ascii=False)
        + "\n\nUser metadata: "
        + json.dumps(
            {"locale": locale, "medical_conditions": medical_conditions, "goals": goals},
            ensure_ascii=False
        )
    )

    plan_text = llm.chat(SYSTEM_PROMPT, prompt)

    plan = _safe_parse_json(plan_text, ["daily_meals", "explanation", "disclaimer"])

    # Reformat retry
    attempts = 0
    while not plan and attempts < 2:
        attempts += 1
        reformatted = llm.chat(
            SYSTEM_PROMPT,
            (
                "Please convert the following output into a JSON object with keys "
                "\"daily_meals\", \"explanation\", \"disclaimer\". Return JSON only.\n\n"
                f"{plan_text}"
            )
        )
        plan = _safe_parse_json(reformatted, ["daily_meals", "explanation", "disclaimer"])

    if not plan:
        return {"type": "error", "message": "Failed to parse meal plan"}

    # ===== Calorie adjust =====
    def _day_total(day_obj: dict) -> float:
        total = 0.0
        for k in ("breakfast", "lunch", "dinner"):
            m = day_obj.get(k)
            if m:
                total += float(m.get("nutrition", {}).get("calories", 0) or 0)
        for s in day_obj.get("snacks") or []:
            total += float(s.get("nutrition", {}).get("calories", 0) or 0)
        return total

    calorie_target = profile.get("calorie_target")
    try:
        ct = float(calorie_target) if calorie_target else None
    except Exception:
        ct = None

    warning = None
    if ct:
        bad_days = []
        for day, obj in plan["daily_meals"].items():
            tot = _day_total(obj)
            if tot == 0 or abs(tot - ct) > ct * 0.05:
                bad_days.append(day)

        if bad_days:
            warning = "Calories may not exactly match target for days: " + ", ".join(bad_days)

    start, end = default_plan_window()
    save_plan(user_id, "meal_plan", plan, start, end)

    resp = {
        "type": "plan_created",
        "message": "New meal plan has been created for this week.",
        "plan": plan
    }
    if warning:
        resp["warning"] = warning

    return resp


def create_workout_plan(llm, user_id: str, profile: Any):
    """
    profile: AIProfileInputDTO
    """

    state = get_user_state(user_id)
    goals = state.get("goals")

    retriever = get_retriever()

    # ===== RAG CONTEXT =====
    try:
        expanded_q = (
            f"workout plan guidance "
            f"experience={profile.experience_level} "
            f"goal={profile.goal} "
            f"days={profile.available_days_per_week}"
        )

        docs = retriever.retrieve(expanded_q, k=6)

        context = "\n\n".join(
            f"[{d['metadata'].get('source')}]\n{d['page_content']}"
            for d in docs
        )
    except Exception:
        context = ""

    # ===== PROMPT =====
    prompt = (
        WORKOUT_PROMPT
        + "\n\nContext:\n" + context
        + "\n\nUser profile:\n"
        + json.dumps(
            {
                "age": profile.age,
                "gender": profile.gender,
                "height_cm": profile.height_cm,
                "weight_kg": profile.weight_kg,
                "experience_level": profile.experience_level,
                "goal": profile.goal,
                "available_days_per_week": profile.available_days_per_week,
                "session_duration_minutes": profile.session_duration_minutes,
                "injuries": profile.injuries,
                "calorie_target": profile.calorie_target,
                "goals": goals
            },
            ensure_ascii=False
        )
    )

    # ===== LLM CALL =====
    plan_text = llm.chat(SYSTEM_PROMPT, prompt)

    plan = _safe_parse_json(
        plan_text,
        ["weekly_schedule", "explanation", "disclaimer"]
    )

    # ===== RETRY JSON PARSE =====
    attempts = 0
    while not plan and attempts < 2:
        attempts += 1
        reformatted = llm.chat(
            SYSTEM_PROMPT,
            (
                "Please convert the following output into a JSON object with keys "
                "\"weekly_schedule\", \"explanation\", \"disclaimer\". "
                "Return JSON only.\n\n"
                f"{plan_text}"
            )
        )

        plan = _safe_parse_json(
            reformatted,
            ["weekly_schedule", "explanation", "disclaimer"]
        )

    if not plan:
        return {
            "type": "error",
            "message": "Failed to parse workout plan"
        }

    # ===== SAVE PLAN =====
    start, end = default_plan_window()
    save_plan(user_id, "workout_plan", plan, start, end)

    return {
        "type": "plan_created",
        "message": "New workout plan has been created for this week.",
        "plan": plan
    }

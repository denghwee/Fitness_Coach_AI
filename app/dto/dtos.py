# dtos.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


class DTOValidationError(ValueError):
    pass


def _pick(d: Dict[str, Any], *keys: str, default=None, required: bool = False):
    """
    Lấy value theo nhiều key (hỗ trợ snake_case và camelCase).
    Ví dụ: _pick(data, "calorie_target", "calorieTarget")
    """
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    if required:
        raise DTOValidationError(f"Missing required field: one of {keys}")
    return default


def _to_int(v: Any, field_name: str) -> int:
    try:
        return int(v)
    except Exception:
        raise DTOValidationError(f"Field '{field_name}' must be int, got: {v!r}")


def _to_float(v: Any, field_name: str) -> float:
    try:
        return float(v)
    except Exception:
        raise DTOValidationError(f"Field '{field_name}' must be number, got: {v!r}")


def _to_str(v: Any, field_name: str) -> str:
    if v is None:
        raise DTOValidationError(f"Field '{field_name}' must be string, got None")
    return str(v)


def _unwrap_payload(data: Any) -> Dict[str, Any]:
    """
    Nhiều service trả kiểu: {"data": {...}} hoặc {"result": {...}}
    -> tự bóc ra cho tiện.
    """
    if not isinstance(data, dict):
        raise DTOValidationError(f"Payload must be object/dict, got: {type(data).__name__}")

    # ưu tiên bóc nếu có key phổ biến
    for k in ("data", "result", "payload"):
        if k in data and isinstance(data[k], dict):
            return data[k]
    return data


@dataclass(frozen=True)
class MealPlanProfileDTO:
    # phục vụ create_meal_plan()
    calorie_target: int
    gender: str
    weight_kg: float
    goal: str

    @staticmethod
    def from_dict(raw: Any) -> "MealPlanProfileDTO":
        d = _unwrap_payload(raw)

        calorie_target = _to_int(
            _pick(d, "calorie_target", "calorieTarget", required=True),
            "calorie_target",
        )
        gender = _to_str(_pick(d, "gender", required=True), "gender")
        weight_kg = _to_float(_pick(d, "weight_kg", "weightKg", required=True), "weight_kg")
        goal = _to_str(_pick(d, "goal", required=True), "goal")

        return MealPlanProfileDTO(
            calorie_target=calorie_target,
            gender=gender,
            weight_kg=weight_kg,
            goal=goal,
        )


from dataclasses import dataclass
from typing import Optional, Any, List


@dataclass(frozen=True)
class WorkoutPlanProfileDTO:
    # phục vụ create_workout_plan()
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    experience_level: str
    available_days_per_week: int

    goal: Optional[str] = None
    session_duration_minutes: Optional[int] = None
    injuries: Optional[List[str]] = None
    calorie_target: Optional[int] = None  # optional

    @staticmethod
    def from_dict(raw: Any) -> "WorkoutPlanProfileDTO":
        d = _unwrap_payload(raw)

        age = _to_int(_pick(d, "age", required=True), "age")
        gender = _to_str(_pick(d, "gender", required=True), "gender")
        height_cm = _to_float(
            _pick(d, "height_cm", "heightCm", required=True),
            "height_cm",
        )
        weight_kg = _to_float(
            _pick(d, "weight_kg", "weightKg", required=True),
            "weight_kg",
        )
        experience_level = _to_str(
            _pick(d, "experience_level", "experienceLevel", required=True),
            "experience_level",
        )

        available_days_per_week = _to_int(
            _pick(d, "available_days_per_week", "availableDaysPerWeek", required=True),
            "available_days_per_week",
        )

        # ✅ goal OPTIONAL – nếu không có thì None
        goal_raw = _pick(d, "goal", default=None)
        goal = None if goal_raw is None else _to_str(goal_raw, "goal")

        session_duration_minutes_raw = _pick(
            d, "session_duration_minutes", "sessionDurationMinutes", default=None
        )
        session_duration_minutes = (
            None
            if session_duration_minutes_raw is None
            else _to_int(session_duration_minutes_raw, "session_duration_minutes")
        )

        injuries_raw = _pick(d, "injuries", default=None)
        if injuries_raw is None:
            injuries = None
        elif isinstance(injuries_raw, list):
            injuries = [str(x) for x in injuries_raw if x is not None]
        else:
            injuries = [str(injuries_raw)]

        calorie_target_raw = _pick(d, "calorie_target", "calorieTarget", default=None)
        calorie_target = (
            None
            if calorie_target_raw is None
            else _to_int(calorie_target_raw, "calorie_target")
        )

        return WorkoutPlanProfileDTO(
            age=age,
            gender=gender,
            height_cm=height_cm,
            weight_kg=weight_kg,
            experience_level=experience_level,
            available_days_per_week=available_days_per_week,
            goal=goal,
            session_duration_minutes=session_duration_minutes,
            injuries=injuries,
            calorie_target=calorie_target,
        )

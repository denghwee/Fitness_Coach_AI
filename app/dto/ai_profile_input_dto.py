from dataclasses import dataclass
from typing import List, Any, Dict


@dataclass
class AIProfileInputDTO:
    age: int
    gender: str
    height_cm: int
    weight_kg: float
    experience_level: str
    goal: str
    available_days_per_week: int
    session_duration_minutes: int
    injuries: List[str]
    calorie_target: int

    @staticmethod
    def from_request(payload: Dict[str, Any]):
        """
        payload = {
            "age": 27,
            "gender": "male",
            ...
        }
        """
        if not payload:
            raise ValueError("Empty payload")

        required_fields = [
            "age",
            "gender",
            "height_cm",
            "weight_kg",
            "experience_level",
            "goal",
            "available_days_per_week",
            "session_duration_minutes",
            "injuries",
            "calorie_target"
        ]

        for field in required_fields:
            if field not in payload:
                raise ValueError(f"Missing field: {field}")

        return AIProfileInputDTO(
            age=int(payload["age"]),
            gender=str(payload["gender"]),
            height_cm=int(payload["height_cm"]),
            weight_kg=float(payload["weight_kg"]),
            experience_level=str(payload["experience_level"]),
            goal=str(payload["goal"]),
            available_days_per_week=int(payload["available_days_per_week"]),
            session_duration_minutes=int(payload["session_duration_minutes"]),
            injuries=list(payload.get("injuries", [])),
            calorie_target=int(payload["calorie_target"])
        )

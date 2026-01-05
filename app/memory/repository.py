from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from app import db
from app.models import UserPlan


class UserStateRepository(ABC):
    """
    Abstract repository cho user state
    """

    @abstractmethod
    def get_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_state(self, user_id: str, state: Dict[str, Any]) -> None:
        pass


class UserStateRepositoryImpl(UserStateRepository):

    def get_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy state của user từ bảng user_plans
        """
        plan: UserPlan | None = (
            db.session.query(UserPlan)
            .filter(UserPlan.user_id == int(user_id))
            .first()
        )

        if not plan:
            return {}

        return {
            "meal_plan": plan.meal_plan,
            "workout_plan": plan.workout_plan
        }

    def save_state(self, user_id: str, state: Dict[str, Any]) -> None:
        """
        UPSERT user_plans (user_id, meal_plan, workout_plan)
        """
        plan: UserPlan | None = (
            db.session.query(UserPlan)
            .filter(UserPlan.user_id == int(user_id))
            .first()
        )

        if not plan:
            # INSERT
            plan = UserPlan(
                user_id=int(user_id),
                meal_plan=state.get("meal_plan"),
                workout_plan=state.get("workout_plan")
            )
            db.session.add(plan)
        else:
            # UPDATE
            if "meal_plan" in state:
                plan.meal_plan = state["meal_plan"]

            if "workout_plan" in state:
                plan.workout_plan = state["workout_plan"]

        db.session.commit()

from app.agent import (
    handle_chat,
    create_meal_plan,
    create_workout_plan
)
from app.memory.store import get_user_state


class AgentService:

    @staticmethod
    def chat(llm, user_id: int, message: str):
        return handle_chat(
            llm=llm,
            user_id=user_id,
            message=message
        )

    # ===== MEAL PLAN =====
    @staticmethod
    def get_meal_plan(user_id: int):
        state = get_user_state(user_id)
        plan = state.get("meal_plan")
        if not plan:
            return {
                "type": "no_plan",
                "message": "No meal plan found"
            }
        return {
            "type": "message",
            "plan": plan["plan"],
            "start_date": plan["start_date"],
            "end_date": plan["end_date"]
        }

    @staticmethod
    def create_meal_plan(llm, user_id: int, goal_input: dict):
        # goal_input hiện đã được chuẩn hóa từ controller
        return create_meal_plan(llm, user_id, goal_input)

    # ===== WORKOUT PLAN =====
    @staticmethod
    def get_workout_plan(user_id: int):
        state = get_user_state(user_id)
        plan = state.get("workout_plan")
        if not plan:
            return {
                "type": "no_plan",
                "message": "No workout plan found"
            }
        return {
            "type": "message",
            "plan": plan["plan"],
            "start_date": plan["start_date"],
            "end_date": plan["end_date"]
        }

    @staticmethod
    def create_workout_plan(llm, user_id: int, profile_input: dict):
        return create_workout_plan(
            llm=llm,
            user_id=user_id,
            profile=profile_input
        )

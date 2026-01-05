# app/services/meal_plan_service.py

from app import db
from app.models.user_plan import UserPlan


class MealPlanService:
    @staticmethod
    def get_by_user_id(user_id: int):
        plan = UserPlan.query.filter_by(user_id=user_id).first()
        if not plan or not plan.meal_plan:
            return None
        return plan.meal_plan
    @staticmethod
    def create(user_id: int, plan: dict):
        user_plan = UserPlan.query.filter_by(user_id=user_id).first()

        if not user_plan:
            user_plan = UserPlan(
                user_id=user_id,
                meal_plan=plan
            )
            db.session.add(user_plan)
        else:
            user_plan.meal_plan = plan

        db.session.commit()
        return plan

    @staticmethod
    def update(user_id: int, plan: dict):
        user_plan = UserPlan.query.filter_by(user_id=user_id).first()

        if not user_plan or not user_plan.meal_plan:
            raise ValueError("Meal plan not found")

        user_plan.meal_plan = plan
        db.session.commit()
        return plan

    @staticmethod
    def delete(user_id: int):
        user_plan = UserPlan.query.filter_by(user_id=user_id).first()

        if not user_plan or not user_plan.meal_plan:
            raise ValueError("Meal plan not found")

        user_plan.meal_plan = None
        db.session.commit()

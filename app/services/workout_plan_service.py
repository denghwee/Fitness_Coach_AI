from app import db
from app.models.user_plan import UserPlan


class WorkoutPlanService:

    @staticmethod
    def get_by_user_id(user_id: int):
        plan = UserPlan.query.filter_by(user_id=user_id).first()
        if not plan or not plan.workout_plan:
            return None
        return plan.workout_plan

    @staticmethod
    def create(user_id: int, workout_plan: dict):
        existing = UserPlan.query.filter_by(user_id=user_id).first()
        if existing and existing.workout_plan:
            raise ValueError("Workout plan already exists")

        if existing:
            existing.workout_plan = workout_plan
        else:
            existing = UserPlan(
                user_id=user_id,
                workout_plan=workout_plan,
            )
            db.session.add(existing)

        db.session.commit()
        return workout_plan

    @staticmethod
    def update(user_id: int, workout_plan: dict):
        plan = UserPlan.query.filter_by(user_id=user_id).first()
        if not plan or not plan.workout_plan:
            raise ValueError("Workout plan not found")

        plan.workout_plan = workout_plan
        db.session.commit()
        return workout_plan

    @staticmethod
    def delete(user_id: int):
        plan = UserPlan.query.filter_by(user_id=user_id).first()
        if not plan or not plan.workout_plan:
            raise ValueError("Workout plan not found")

        plan.workout_plan = None
        db.session.commit()

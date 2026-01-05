from app import db
from sqlalchemy.dialects.mysql import JSON

class UserPlan(db.Model):
    __tablename__ = "user_plans"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False, unique=True)

    meal_plan = db.Column(JSON)
    workout_plan = db.Column(JSON)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )


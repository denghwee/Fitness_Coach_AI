from flask import Blueprint, request, jsonify
from app.agent import (
handle_chat,
create_meal_plan,
create_workout_plan
)
from app.llm import get_llm

agent_bp = Blueprint("agent", __name__, url_prefix="/agent")
llm = get_llm()


@agent_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    return jsonify(handle_chat(
        llm=llm,
        user_id=data["user_id"],
        message=data["message"]
    ))


@agent_bp.route("/meal-plan", methods=["POST"])
def meal_plan():
    data = request.get_json()
    return jsonify(create_meal_plan(llm, data["user_id"]))


@agent_bp.route("/workout-plan", methods=["POST"])
def workout_plan():
    data = request.get_json()
    return jsonify(create_workout_plan(llm, data["user_id"]))
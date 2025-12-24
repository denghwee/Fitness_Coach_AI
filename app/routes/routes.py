from flask import Blueprint, request, jsonify
from app.agent import (
    handle_chat,
    create_meal_plan,
    create_workout_plan
)
from app.llm import get_llm
from app.memory.store import get_user_state

agent_bp = Blueprint("agent", __name__, url_prefix="/api/v3/agent")
llm = get_llm()


@agent_bp.route("/chat", methods=["OPTIONS", "POST"])
def chat():
    if request.method == "OPTIONS":
        return ('', 204)
    data = request.get_json()
    return jsonify(handle_chat(
        llm=llm,
        user_id=data["user_id"],
        message=data["message"]
    ))


@agent_bp.route("/meal-plan", methods=["OPTIONS", "GET", "POST"])
def meal_plan():
    if request.method == "OPTIONS":
        return ('', 204)

    if request.method == "GET":
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id missing"}), 400
        state = get_user_state(user_id)
        plan = state.get("meal_plan")
        if not plan:
            return jsonify({"type": "no_plan", "message": "No meal plan found"}), 200
        return jsonify({
            "type": "message",
            "plan": plan["plan"],
            "start_date": plan["start_date"],
            "end_date": plan["end_date"]
        })

    # POST
    data = request.get_json()
    return jsonify(create_meal_plan(llm, data["user_id"]))


@agent_bp.route("/workout-plan", methods=["OPTIONS", "GET", "POST"])
def workout_plan():
    if request.method == "OPTIONS":
        return ('', 204)

    if request.method == "GET":
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id missing"}), 400
        state = get_user_state(user_id)
        plan = state.get("workout_plan")
        if not plan:
            return jsonify({"type": "no_plan", "message": "No workout plan found"}), 200
        return jsonify({
            "type": "message",
            "plan": plan["plan"],
            "start_date": plan["start_date"],
            "end_date": plan["end_date"]
        })

    # POST
    data = request.get_json()
    return jsonify(create_workout_plan(llm, data["user_id"]))
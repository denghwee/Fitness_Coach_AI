
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt
from app.controllers.agent_controller import AgentController

agent_bp = Blueprint("agent", __name__, url_prefix="/api/v3/agent")





# ===== CHAT =====
@agent_bp.route("/chat", methods=["OPTIONS", "POST"])
@jwt_required()
def chat():
    if hasattr(chat, "method") and chat.method == "OPTIONS":
        return "", 204
    return AgentController.chat()


@agent_bp.route("/workout-plan", methods=["OPTIONS", "GET", "POST"])
@jwt_required()
def workout_plan():
    if request.method == "OPTIONS":
        return "", 204

    if request.method == "GET":
        return AgentController.get_workout_plan()

    # POST
    return AgentController.create_workout_plan()


@agent_bp.route("/meal-plan", methods=["OPTIONS", "GET", "POST"])
@jwt_required()
def meal_plan():
    if request.method == "OPTIONS":
        return "", 204

    if request.method == "GET":
        return AgentController.get_meal_plan()

    # POST
    return AgentController.create_meal_plan()


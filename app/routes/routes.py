from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from app.agent import (
    handle_chat,
    create_meal_plan,
    create_workout_plan
)
from app.dto.ai_profile_input_dto import AIProfileInputDTO
from app.llm import get_llm
from app.memory.store import get_user_state

agent_bp = Blueprint("agent", __name__, url_prefix="/api/v3/agent")
llm = get_llm()

# ===== Helper function lấy userId từ JWT =====
def get_user_id_from_token():
    claims = get_jwt()
    user_id = claims.get("userId")  # auth-service phải set custom claim này
    if not user_id:
        return None
    return user_id


# ===== CHAT ENDPOINT =====
@agent_bp.route("/chat", methods=["OPTIONS", "POST"])
@jwt_required()
def chat():
    if request.method == "OPTIONS":
        return ('', 204)

    data = request.get_json()
    token_user_id = get_user_id_from_token()

    # Nếu client gửi user_id, kiểm tra trùng với token
    if "user_id" in data and data["user_id"] != token_user_id:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(handle_chat(
        llm=llm,
        user_id=token_user_id,
        message=data["message"]
    ))


# ===== MEAL PLAN ENDPOINT =====
@agent_bp.route("/meal-plan", methods=["OPTIONS", "GET", "POST"])
@jwt_required()
def meal_plan():
    if request.method == "OPTIONS":
        return ('', 204)

    token_user_id = get_user_id_from_token()

    if request.method == "GET":
        # GET user_id từ query nếu cần, nhưng sẽ ưu tiên token
        user_id = request.args.get("user_id") or token_user_id
        if not user_id:
            return jsonify({"error": "user_id missing"}), 400

        if user_id != token_user_id:
            return jsonify({"error": "Unauthorized"}), 403

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
    user_id = data.get("user_id") or token_user_id
    if user_id != token_user_id:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(create_meal_plan(llm, user_id))


@agent_bp.route("/workout-plan", methods=["OPTIONS", "GET", "POST"])
@jwt_required()
def workout_plan():
    if request.method == "OPTIONS":
        return "", 204

    token_user_id = get_user_id_from_token()

    # ========= GET =========
    if request.method == "GET":
        user_id = request.args.get("user_id") or token_user_id
        if not user_id:
            return jsonify({"error": "user_id missing"}), 400

        if user_id != token_user_id:
            return jsonify({"error": "Unauthorized"}), 403

        state = get_user_state(user_id)
        plan = state.get("workout_plan")

        if not plan:
            return jsonify({
                "type": "no_plan",
                "message": "No workout plan found"
            }), 200

        return jsonify({
            "type": "message",
            "plan": plan["plan"],
            "start_date": plan["start_date"],
            "end_date": plan["end_date"]
        }), 200

    # ========= POST =========
    try:
        payload = request.get_json()
        profile_dto = AIProfileInputDTO.from_request(payload)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    result = create_workout_plan(
        llm=llm,
        user_id=token_user_id,
        profile=profile_dto
    )

    return jsonify(result), 200


from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.llm import get_llm
from app.services.agent_service import AgentService
from app.clients.user_profile_client import UserProfileClient
from app.utils.jwt_utils import get_access_token, get_user_id_from_token

llm = get_llm()


class AgentController:

    # =========================
    # CHAT
    # =========================
    @staticmethod
    @jwt_required()
    def chat():
        data = request.get_json()
        user_id = get_user_id_from_token()

        if not data or "message" not in data:
            return jsonify({"error": "Message is required"}), 400

        if "user_id" in data and data["user_id"] != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        result = AgentService.chat(
            llm=llm,
            user_id=user_id,
            message=data["message"]
        )
        return jsonify(result), 200

    # =========================
    # MEAL PLAN
    # =========================
    @staticmethod
    @jwt_required()
    def get_meal_plan():
        user_id = get_user_id_from_token()
        result = AgentService.get_meal_plan(user_id)
        return jsonify(result), 200

    @staticmethod
    @jwt_required()
    def create_meal_plan():
        user_id = get_user_id_from_token()
        access_token = get_access_token(request)

        try:
            goal_input = UserProfileClient.get_ai_goal_input(
                access_token=access_token
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception:
            return jsonify({"error": "User profile service unavailable"}), 503

        result = AgentService.create_meal_plan(
            llm=llm,
            user_id=user_id,
            goal_input=goal_input
        )
        return jsonify(result), 200

    # =========================
    # WORKOUT PLAN
    # =========================
    @staticmethod
    @jwt_required()
    def get_workout_plan():
        user_id = get_user_id_from_token()
        result = AgentService.get_workout_plan(user_id)
        return jsonify(result), 200

    @staticmethod
    @jwt_required()
    def create_workout_plan():
        user_id = get_user_id_from_token()
        access_token = get_access_token(request)

        try:
            profile_input = UserProfileClient.get_ai_profile_input(
                access_token=access_token
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception:
            return jsonify({"error": "User profile service unavailable"}), 503



        result = AgentService.create_workout_plan(
            llm=llm,
            user_id=user_id,
            profile_input=profile_input
        )
        return jsonify(result), 200

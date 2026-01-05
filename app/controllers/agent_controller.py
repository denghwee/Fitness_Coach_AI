from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.dto.dtos import MealPlanProfileDTO, DTOValidationError, WorkoutPlanProfileDTO
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
    def create_workout_plan():
        user_id = get_user_id_from_token()
        access_token = get_access_token(request)

        try:
            profile_json = UserProfileClient.get_ai_profile_input(
                access_token=access_token
            )
            profile_dto = WorkoutPlanProfileDTO.from_dict(profile_json)
        except DTOValidationError as e:
            return jsonify({"error": str(e)}), 400
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception:
            return jsonify({"error": "User profile service unavailable"}), 503

        result = AgentService.create_workout_plan(
            llm=llm,
            user_id=user_id,
            profile_input=profile_dto,  # ✅ DTO
        )
        return jsonify(result), 200

    @staticmethod
    @jwt_required()
    def create_meal_plan():
        user_id = get_user_id_from_token()
        access_token = get_access_token(request)

        try:
            goal_json = UserProfileClient.get_ai_goal_input(
                access_token=access_token
            )
            goal_dto = MealPlanProfileDTO.from_dict(goal_json)
        except DTOValidationError as e:
            return jsonify({"error": str(e)}), 400
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception:
            return jsonify({"error": "User profile service unavailable"}), 503

        result = AgentService.create_meal_plan(
            llm=llm,
            user_id=user_id,
            goal_input=goal_dto,  # ✅ DTO
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
    def post_workout_plan():
        user_id = get_user_id_from_token()
        data = request.get_json()

        if not data or "plan" not in data:
            return jsonify({"error": "Workout plan payload is required"}), 400

        try:
            from app.services.workout_plan_service import WorkoutPlanService
            plan = WorkoutPlanService.create(user_id, data["plan"])
            return jsonify({
                "type": "plan_created",
                "message": "Workout plan created successfully",
                "plan": plan
            }), 201

        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @staticmethod
    @jwt_required()
    def put_workout_plan():
        user_id = get_user_id_from_token()
        data = request.get_json()

        if not data or "plan" not in data:
            return jsonify({"error": "Workout plan payload is required"}), 400

        try:
            from app.services.workout_plan_service import WorkoutPlanService
            plan = WorkoutPlanService.update(user_id, data["plan"])
            return jsonify({
                "type": "plan_updated",
                "message": "Workout plan updated successfully",
                "plan": plan
            }), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    @staticmethod
    @jwt_required()
    def delete_workout_plan():
        user_id = get_user_id_from_token()

        try:
            from app.services.workout_plan_service import WorkoutPlanService
            WorkoutPlanService.delete(user_id)
            return jsonify({
                "type": "plan_deleted",
                "message": "Workout plan deleted successfully"
            }), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    @staticmethod
    @jwt_required()
    def post_meal_plan():
        user_id = get_user_id_from_token()
        data = request.get_json()

        if not data or "plan" not in data:
            return jsonify({"error": "Meal plan payload is required"}), 400

        try:
            from app.services.meal_plan_service import MealPlanService
            plan = MealPlanService.create(user_id, data["plan"])
            return jsonify({
                "type": "plan_created",
                "message": "Meal plan created successfully",
                "plan": plan
            }), 201

        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @staticmethod
    @jwt_required()
    def put_meal_plan():
        user_id = get_user_id_from_token()
        data = request.get_json()

        if not data or "plan" not in data:
            return jsonify({"error": "Meal plan payload is required"}), 400

        try:
            from app.services.meal_plan_service import MealPlanService
            plan = MealPlanService.update(user_id, data["plan"])
            return jsonify({
                "type": "plan_updated",
                "message": "Meal plan updated successfully",
                "plan": plan
            }), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 404

    @staticmethod
    @jwt_required()
    def delete_meal_plan():
        user_id = get_user_id_from_token()

        try:
            from app.services.meal_plan_service import MealPlanService
            MealPlanService.delete(user_id)
            return jsonify({
                "type": "plan_deleted",
                "message": "Meal plan deleted successfully"
            }), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 404

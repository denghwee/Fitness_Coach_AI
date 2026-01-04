import os
import requests


class UserProfileClient:
    BASE_URL = os.getenv(
        "USER_PROFILE_SERVICE_URL",
        "http://localhost:8080/api/v2/user-profile"
    )

    @staticmethod
    def get_ai_profile_input(access_token: str):
        resp = requests.get(
            f"{UserProfileClient.BASE_URL}/ai/profile-input",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def get_ai_goal_input(access_token: str):
        resp = requests.get(
            f"{UserProfileClient.BASE_URL}/ai/goal-input",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5
        )
        resp.raise_for_status()
        return resp.json()

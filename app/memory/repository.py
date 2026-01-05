from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class UserStateRepository(ABC):
    """
    Abstract repository cho user state
    """

    @abstractmethod
    def get_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_state(self, user_id: str, state: Dict[str, Any]) -> None:
        pass

class UserStateRepositoryImpl(UserStateRepository):

    def get_state(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        TODO:
        - SELECT state_json FROM user_state WHERE user_id = ?
        """
        raise NotImplementedError

    def save_state(self, user_id: str, state: Dict[str, Any]) -> None:
        """
        TODO:
        - UPSERT user_state (user_id, state_json, updated_at)
        """
        raise NotImplementedError

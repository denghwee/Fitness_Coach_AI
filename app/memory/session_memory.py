# session_memory.py
import time
from typing import Dict, Any

SESSION_TTL_SECONDS = 30 * 60  # 30 phút

_session_store: Dict[str, Dict[str, Any]] = {}


def _now() -> float:
    return time.time()


def get_session_memory(user_id: str) -> Dict[str, Any]:
    session = _session_store.get(user_id)

    if not session:
        return {}

    if _now() - session["updated_at"] > SESSION_TTL_SECONDS:
        _session_store.pop(user_id, None)
        return {}

    return session["data"]


def update_session_memory(user_id: str, data: Dict[str, Any]) -> None:
    _session_store[user_id] = {
        "data": data,
        "updated_at": _now(),
    }

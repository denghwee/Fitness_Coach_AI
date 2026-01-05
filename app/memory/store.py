from datetime import date
import json
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict

from .repository import UserStateRepository, UserStateRepositoryImpl

# ==============================
# Config
# ==============================

_repo: UserStateRepository = UserStateRepositoryImpl()

_BASE_DIR = Path.cwd() / "data" / "memory"
_BASE_DIR.mkdir(parents=True, exist_ok=True)


def _user_path(user_id: str) -> Path:
    return _BASE_DIR / f"{user_id}.json"


# ==============================
# Helpers
# ==============================

def _to_iso(d: Any) -> Any:
    try:
        if hasattr(d, "isoformat"):
            return d.isoformat()
    except Exception:
        pass
    return d


# ==============================
# Lazy load + cache
# ==============================

@lru_cache(maxsize=1024)
def _load_user_state(user_id: str) -> Dict[str, Any]:
    """
    Load state từ DB (cached)
    """
    state = _repo.get_state(user_id)
    return state or {}

def _save_user_state(user_id: str, state: Dict[str, Any]) -> None:
    path = _user_path(user_id)
    tmp = path.with_suffix(".tmp")

    try:
        tmp.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        tmp.replace(path)
    finally:
        # invalidate cache cho user này
        _load_user_state.cache_clear()


# ==============================
# Public API
# ==============================

def get_user_state(user_id: str) -> Dict[str, Any]:
    """
    Trả về state của user.
    Nếu chưa tồn tại → {}
    """
    return _load_user_state(user_id).copy()


def save_plan(user_id: str, plan_type: str, plan: dict, start, end) -> None:
    """
    Lưu meal_plan / workout_plan cho user
    """
    state = _load_user_state(user_id).copy()

    state[plan_type] = {
        "plan": plan,
        "start_date": _to_iso(start),
        "end_date": _to_iso(end),
    }

    _repo.save_state(user_id, state)

    # invalidate cache cho user này
    _load_user_state.cache_clear()


def is_plan_active(state: dict, plan_type: str) -> bool:
    """
    Check plan còn hiệu lực hay không
    """
    if not state or plan_type not in state:
        return False

    today = date.today().isoformat()

    try:
        return today <= state[plan_type]["end_date"]
    except Exception:
        return False

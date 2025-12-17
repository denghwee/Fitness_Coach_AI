from datetime import date
import json
from pathlib import Path
from typing import Any, Dict

# In-memory cache
_MEMORY: Dict[str, Dict[str, Any]] = {}

# Persistence file (project-root `data` folder)
_STORE_PATH = Path.cwd() / "data" / "memory_store.json"
_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_from_disk() -> None:
    global _MEMORY
    try:
        if _STORE_PATH.exists():
            with open(_STORE_PATH, "r", encoding="utf-8") as f:
                _MEMORY = json.load(f)
        else:
            _MEMORY = {}
    except Exception:
        # on any error, start with empty memory
        _MEMORY = {}


def _save_to_disk() -> None:
    tmp = _STORE_PATH.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(_MEMORY, f, ensure_ascii=False, indent=2)
        tmp.replace(_STORE_PATH)
    except Exception:
        # best-effort: ignore persistence failures
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass


# load persisted memory on import
_load_from_disk()


def get_user_state(user_id: str) -> dict:
    return _MEMORY.get(user_id, {})


def _to_iso(d: Any) -> Any:
    try:
        if hasattr(d, "isoformat"):
            return d.isoformat()
    except Exception:
        pass
    return d


def save_plan(user_id: str, plan_type: str, plan: dict, start, end) -> None:
    state = _MEMORY.setdefault(user_id, {})
    state[plan_type] = {
        "plan": plan,
        "start_date": _to_iso(start),
        "end_date": _to_iso(end),
    }
    _save_to_disk()


def is_plan_active(state: dict, plan_type: str) -> bool:
    if plan_type not in state:
        return False
    today = date.today().isoformat()
    try:
        return today <= state[plan_type]["end_date"]
    except Exception:
        return False
from typing import Any

def safe_cast_float(v: Any, default: float = 1.0) -> float:
    try:
        return float(v)
    except Exception:
        return default

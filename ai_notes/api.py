import functools
import time
from flask import Blueprint, request, jsonify
from .services.ai_router import AIRouter
from .utils.logging import redact_pii

bp = Blueprint("api", __name__)


_rate_limiter = {}


def ratelimit(key: str, limit_per_minute=10):
    now = time.time()
    window = 60
    lst = _rate_limiter.get(key, [])
    lst = [t for t in lst if now - t < window]
    if len(lst) >= limit_per_minute:
        return False
    lst.append(now)
    _rate_limiter[key] = lst
    return True


def require_ai_ratelimit(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        key = request.remote_addr or "anon"
        if not ratelimit(key):
            return jsonify({"error": "rate_limited"}), 429
        return f(*args, **kwargs)

    return wrapper


@bp.post("/ai/interpret")
@require_ai_ratelimit
def ai_interpret():
    data = request.get_json(silent=True) or {}
    utterance = (data.get("utterance") or "").strip()
    context = data.get("context") or {}
    tz = context.get("now_tz") or "Asia/Kuwait"
    if not utterance:
        return jsonify({"error": "empty_utterance"}), 400
    router = AIRouter()
    parsed = router.build_action(utterance, tz=tz, user_id="demo")
    try:
        from flask import current_app

        current_app.logger.info({
            "ai_interpret": {
                "utterance": redact_pii(utterance),
                "parsed": parsed,
            }
        })
    except Exception:
        pass
    return jsonify(parsed)

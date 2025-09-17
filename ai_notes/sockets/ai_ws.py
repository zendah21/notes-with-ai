from flask import Blueprint, render_template
from flask_sock import Sock
import json
from ..services.ai_router import AIRouter
from ..utils.logging import redact_pii

bp = Blueprint("ai_ws", __name__)
sock = Sock()


@bp.route("/ai/console")
def ai_console():
    return render_template("ai/console.html")


@sock.route("/ws/ai")
def ai_ws(ws):
    router = AIRouter()
    while True:
        raw = ws.receive()
        if raw is None:
            break
        try:
            data = json.loads(raw)
        except Exception:
            ws.send(json.dumps({"phase": "error", "message": "invalid_json"}))
            continue
        choose_id = data.get("choose_id")
        utterance = (data.get("utterance") or "").strip()
        tz = (data.get("context") or {}).get("now_tz") or "Asia/Kuwait"
        if not utterance:
            ws.send(json.dumps({"phase": "error", "message": "empty_utterance"}))
            continue
        ws.send(json.dumps({"phase": "thinking"}))
        parsed = router.build_action(utterance, tz=tz, user_id="demo")
        if choose_id:
            parsed["target"] = {"by": "id", "value": int(choose_id)}
        try:
            from flask import current_app
            current_app.logger.info({
                "ws_ai": {
                    "utterance": redact_pii(utterance),
                    "parsed": parsed,
                }
            })
        except Exception:
            pass
        ws.send(json.dumps({"phase": "parsed", "json": parsed}))
        # Clarification: multiple matches by title
        try:
            tgt = (parsed.get("target") or {})
            if tgt.get("by") == "title" and tgt.get("value"):
                from ..models import Task
                v = str(tgt.get("value")).lower()
                matches = Task.query.filter(Task.title.ilike(f"%{v}%")).all()
                if len(matches) > 1:
                    ws.send(json.dumps({
                        "phase": "need_clarification",
                        "options": [{"id": t.id, "title": t.title} for t in matches],
                    }))
                    # wait for next message to receive choose_id
                    continue
        except Exception:
            pass
        try:
            task = router.apply_action(parsed)
        except Exception as e:
            ws.send(json.dumps({"phase": "error", "message": str(e)}))
            continue
        ws.send(json.dumps({"phase": "applied", "task_id": getattr(task, 'id', None)}))
        # send row patch
        from flask import current_app
        with current_app.app_context():
            from ..models import Task
            from flask import render_template

            t = Task.query.get(getattr(task, "id", None))
            if t is not None:
                html = render_template("tasks/item_row.html", task=t)
                ws.send(json.dumps({"phase": "patch", "task_id": t.id, "html": html}))

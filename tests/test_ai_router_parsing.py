import json
from ai_notes.services.ai_router import AIRouter


def test_rule_parsing_duration_priority_notifications(monkeypatch):
    r = AIRouter()
    u = "Move the Rise email to Friday 9:30, set high, 20m, alert 1h"

    # monkeypatch HF calls to avoid network
    monkeypatch.setattr("ai_notes.services.ai_router.hf_zero_shot", lambda t, labels: ("update", {}))
    monkeypatch.setattr("ai_notes.services.ai_router.hf_ner", lambda t: [])
    monkeypatch.setattr("ai_notes.services.ai_router.hf_text2json", lambda p: {})

    parsed = r.build_action(u, tz="Asia/Kuwait", user_id="demo")
    assert parsed["operation"] in {"update", "create"}
    f = parsed["fields"]
    assert f["estimated_duration_minutes"] == 20
    assert f["priority"] == "high"
    assert f["notify_offsets_minutes"] == [60]



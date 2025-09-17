from ai_notes.services.ai_router import AIRouter
from app import create_app


def test_create_update_complete_flow():
    app = create_app()
    with app.app_context():
        r = AIRouter()
        # create
        action = {
            "operation": "create",
            "target": {"by": "title", "value": "Rise email"},
            "fields": {"priority": "high"},
        }
        t = r.apply_action(action)
        assert t.id is not None

        # update
        action["operation"] = "update"
        action["target"] = {"by": "id", "value": t.id}
        action["fields"] = {"estimated_duration_minutes": 20}
        t = r.apply_action(action)
        assert t.estimated_duration_minutes == 20

        # complete
        action = {"operation": "complete", "target": {"by": "id", "value": t.id}, "fields": {}}
        t = r.apply_action(action)
        assert t.status == "done"


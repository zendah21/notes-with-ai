import os
import json
import textwrap
import streamlit as st
from dotenv import load_dotenv


@st.cache_resource
def _init_flask_app():
    load_dotenv()
    # Bridge Streamlit secrets → env for HF
    os.environ.setdefault("HF_API_TOKEN", st.secrets.get("HF_API_TOKEN", os.getenv("HF_API_TOKEN", "")))
    os.environ.setdefault("HF_TASK_MODEL_TEXT2TEXT", st.secrets.get("HF_TASK_MODEL_TEXT2TEXT", os.getenv("HF_TASK_MODEL_TEXT2TEXT", "google/flan-t5-base")))
    os.environ.setdefault("HF_CLASSIFIER_MODEL_ZEROSHOT", st.secrets.get("HF_CLASSIFIER_MODEL_ZEROSHOT", os.getenv("HF_CLASSIFIER_MODEL_ZEROSHOT", "facebook/bart-large-mnli")))
    os.environ.setdefault("HF_NER_MODEL", st.secrets.get("HF_NER_MODEL", os.getenv("HF_NER_MODEL", "dslim/bert-base-NER")))

    from app import create_app

    flask_app = create_app()
    return flask_app


def _badge(text, color):
    return f"<span class='badge rounded-pill text-bg-{color}' style='margin-right:6px'>{text}</span>"


def _render_task_card(task):
    # Build small HTML card similar to Bootstrap styling via Streamlit components
    title = task.title
    pr = task.priority or "medium"
    st_map = {"low": "secondary", "medium": "secondary", "high": "warning", "urgent": "danger"}
    pr_badge = _badge(pr, st_map.get(pr, "secondary"))
    st_cls = {"pending": "secondary", "in_progress": "info", "done": "success"}.get(task.status or "pending", "secondary")
    st_badge = _badge(task.status.replace("_", " "), st_cls)
    dur = f"⏱ {task.estimated_duration_minutes}m" if task.estimated_duration_minutes else ""
    dl = task.deadline_utc.strftime("%Y-%m-%d %H:%M") + " UTC" if task.deadline_utc else ""
    tags = ", ".join(task.tag_list())
    alerts = ", ".join([f"{m}m" if m < 60 else f"{m//60}h" for m in task.notify_list()])
    btn_label = "Reopen" if task.status == "done" else "Complete"

    st.markdown(
        f"""
        <div style='border:1px solid #ddd;border-radius:8px;padding:12px;margin-bottom:10px;'>
          <div style='display:flex;justify-content:space-between;align-items:center;'>
            <div><strong>{title}</strong></div>
            <div>{st_badge}</div>
          </div>
          <div style='margin-top:6px;'>{pr_badge}{_badge(dur,'light') if dur else ''}{_badge('📅 '+dl,'light') if dl else ''}</div>
          {f"<div style='margin-top:6px;color:#4a5568;white-space:pre-wrap;'>{task.description}</div>" if (getattr(task,'description',None)) else ''}
          {f"<div style='margin-top:6px;color:#666;'># " + tags + "</div>" if tags else ''}
          {f"<div style='margin-top:6px;color:#666;'>🔔 Alerts: " + alerts + "</div>" if alerts else ''}
          <div style='margin-top:10px;'>
            <form action='/tasks/{task.id}/toggle' method='get'>
              <button type='submit'>{btn_label}</button>
            </form>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="AI Notes (Streamlit)", page_icon="📝", layout="centered")
    app = _init_flask_app()
    from ai_notes.services.ai_router import AIRouter
    from ai_notes.models import Task

    st.title("AI Notes – Streamlit Console")
    st.caption("Create/update tasks with natural language. Times are saved in UTC.")

    utter = st.text_input("Command", placeholder="e.g., Create 'Write polite rejection email' tomorrow 10am, 30m, high, alerts 12h and 1h")
    tz = st.selectbox("Timezone for parsing", ["Asia/Kuwait", "UTC", "Asia/Dubai", "Europe/London", "America/New_York"], index=0)
    go = st.button("Interpret and Apply")

    with app.app_context():
        router = AIRouter()
        if go and utter.strip():
            st.write("Thinking…")
            parsed = router.build_action(utter.strip(), tz=tz, user_id="demo")
            st.subheader("Parsed Action")
            st.code(json.dumps(parsed, indent=2))
            try:
                task = router.apply_action(parsed)
                st.success(f"Applied operation: {parsed.get('operation')} → task #{getattr(task,'id', '?')}")
            except Exception as e:
                st.error(f"Apply failed: {e}")

        st.subheader("Tasks")
        tasks = Task.query.order_by(Task.deadline_utc.asc().nullslast()).all()
        for t in tasks:
            _render_task_card(t)


if __name__ == "__main__":
    main()

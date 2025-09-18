from flask import Blueprint, render_template, request, redirect, url_for, Response
from .models import Task
from .db import db
from .scheduler import on_task_changed
from .utils.time import parse_natural_datetime, to_utc_iso

bp = Blueprint("routes", __name__)


@bp.get("/help")
def help_page():
    return render_template("help.html")


@bp.route("/tasks/create", methods=["POST"])
def create_task():
    title = request.form.get("title", "").strip()
    if not title:
        return redirect(url_for("index"))
    t = Task(title=title)
    db.session.add(t)
    db.session.commit()
    on_task_changed(t)
    if request.headers.get("HX-Request"):
        return render_template("tasks/item_row.html", task=t)
    return redirect(url_for("index"))


@bp.route("/tasks/<int:task_id>/toggle", methods=["GET", "POST"])
def toggle_task(task_id: int):
    t = Task.query.get_or_404(task_id)
    t.status = "done" if t.status != "done" else "pending"
    db.session.commit()
    on_task_changed(t)
    if request.headers.get("HX-Request"):
        return render_template("tasks/item_row.html", task=t)
    return redirect(url_for("index"))


@bp.post("/tasks/<int:task_id>/status")
def set_status(task_id: int):
    t = Task.query.get_or_404(task_id)
    val = (request.form.get("status") or "").strip()
    if val in {"pending", "in_progress", "done"}:
        t.status = val
        db.session.commit()
        on_task_changed(t)
    if request.headers.get("HX-Request"):
        return render_template("tasks/item_row.html", task=t)
    return redirect(url_for("index"))


@bp.post("/tasks/<int:task_id>/priority")
def set_priority(task_id: int):
    t = Task.query.get_or_404(task_id)
    val = (request.form.get("priority") or "").strip()
    if val in {"low", "medium", "high", "urgent"}:
        t.priority = val
        db.session.commit()
        on_task_changed(t)
    if request.headers.get("HX-Request"):
        return render_template("tasks/item_row.html", task=t)
    return redirect(url_for("index"))


@bp.post("/tasks/<int:task_id>/deadline")
def set_deadline(task_id: int):
    tz = request.form.get("tz") or "Asia/Kuwait"
    text = (request.form.get("deadline_text") or "").strip()
    t = Task.query.get_or_404(task_id)
    if text:
        try:
            dt = parse_natural_datetime(text, default_tz=tz)
            from dateutil import tz as dzt
            t.deadline_utc = dt.astimezone(dzt.UTC).replace(tzinfo=None)
        except Exception:
            pass
    else:
        t.deadline_utc = None
    db.session.commit()
    on_task_changed(t)
    if request.headers.get("HX-Request"):
        return render_template("tasks/item_row.html", task=t)
    return redirect(url_for("index"))


@bp.post("/tasks/<int:task_id>/duration")
def set_duration(task_id: int):
    t = Task.query.get_or_404(task_id)
    try:
        val = int(request.form.get("minutes") or 0)
        t.estimated_duration_minutes = val or None
    except Exception:
        pass
    db.session.commit()
    on_task_changed(t)
    if request.headers.get("HX-Request"):
        return render_template("tasks/item_row.html", task=t)
    return redirect(url_for("index"))


@bp.post("/tasks/<int:task_id>/alerts")
def set_alerts(task_id: int):
    t = Task.query.get_or_404(task_id)
    raw = (request.form.get("alerts") or "").strip()
    mins = []
    if raw:
        import re

        for m in re.finditer(r"(\d+)\s*(h|hour|hours|m|min|minute)?", raw, re.I):
            n = int(m.group(1))
            unit = (m.group(2) or "m").lower()
            mins.append(n * 60 if unit.startswith("h") else n)
    t.notify_offsets_minutes = ",".join(str(x) for x in sorted({int(x) for x in mins})) if mins else None
    db.session.commit()
    on_task_changed(t)
    if request.headers.get("HX-Request"):
        return render_template("tasks/item_row.html", task=t)
    return redirect(url_for("index"))


@bp.post("/tasks/<int:task_id>/edit")
def edit_task(task_id: int):
    t = Task.query.get_or_404(task_id)
    title = (request.form.get("title") or t.title).strip()
    desc = (request.form.get("description") or "").strip()
    t.title = title or t.title
    t.description = desc or None
    db.session.commit()
    on_task_changed(t)
    if request.headers.get("HX-Request"):
        return render_template("tasks/item_row.html", task=t)
    return redirect(url_for("index"))


@bp.post("/tasks/<int:task_id>/delete")
def delete_task(task_id: int):
    t = Task.query.get_or_404(task_id)
    db.session.delete(t)
    db.session.commit()
    if request.headers.get("HX-Request"):
        return Response("", status=200)
    return redirect(url_for("index"))


@bp.delete("/tasks/<int:task_id>")
def delete_task_delete(task_id: int):
    t = Task.query.get_or_404(task_id)
    db.session.delete(t)
    db.session.commit()
    return Response("", status=204)


@bp.route("/tasks/<int:task_id>/row")
def task_row(task_id: int):
    t = Task.query.get_or_404(task_id)
    return render_template("tasks/item_row.html", task=t)

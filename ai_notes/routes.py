from flask import Blueprint, render_template, request, redirect, url_for, Response
from .models import Task
from .db import db
from .scheduler import on_task_changed

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

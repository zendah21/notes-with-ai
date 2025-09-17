from flask import Blueprint, render_template, request, redirect, url_for
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
    return redirect(url_for("index"))


@bp.route("/tasks/<int:task_id>/toggle")
def toggle_task(task_id: int):
    t = Task.query.get_or_404(task_id)
    t.status = "done" if t.status != "done" else "pending"
    db.session.commit()
    on_task_changed(t)
    return redirect(url_for("index"))


@bp.route("/tasks/<int:task_id>/row")
def task_row(task_id: int):
    t = Task.query.get_or_404(task_id)
    return render_template("tasks/item_row.html", task=t)

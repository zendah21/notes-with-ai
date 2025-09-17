import os
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from flask import current_app
from .models import Task
from .db import db


_scheduler = None


def _send_notification(task_id: int, offset_min: int):
    # Placeholder: In real app, integrate with email/push.
    current_app.logger.info(f"[notify] Task {task_id} offset {offset_min}m")


def _schedule_task_notifications(task: Task):
    global _scheduler
    if not _scheduler:
        return
    # Remove existing jobs for this task
    for job in list(_scheduler.get_jobs()):
        if job.name and job.name.startswith(f"task-{task.id}-"):
            _scheduler.remove_job(job.id)

    if not task.deadline_utc:
        return
    for offset in task.notify_list():
        when = task.deadline_utc - timedelta(minutes=offset)
        if when > datetime.utcnow():
            _scheduler.add_job(
                _send_notification,
                trigger=DateTrigger(run_date=when),
                args=[task.id, offset],
                name=f"task-{task.id}-notify-{offset}",
                replace_existing=True,
            )


def reschedule_all():
    from .models import Task

    tasks = Task.query.all()
    for t in tasks:
        _schedule_task_notifications(t)


def init_scheduler(app):
    global _scheduler
    if _scheduler:
        return
    # Avoid starting scheduler in the reloader parent process
    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return
    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.start()
    # Shutdown on process exit instead of per-request teardown
    atexit.register(lambda: _scheduler.shutdown(wait=False))
    with app.app_context():
        reschedule_all()


def on_task_changed(task: Task):
    _schedule_task_notifications(task)

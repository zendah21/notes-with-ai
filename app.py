import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from ai_notes.db import init_db, db
from ai_notes.scheduler import init_scheduler
from ai_notes.routes import bp as routes_bp
from ai_notes.api import bp as api_bp
from ai_notes.sockets.ai_ws import sock, bp as ws_bp


def create_app():
    load_dotenv()
    base_dir = os.path.dirname(__file__)
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "ai_notes", "templates"),
        static_folder=os.path.join(base_dir, "ai_notes", "static"),
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///ai_notes.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

    init_db(app)
    init_scheduler(app)

    # Blueprints
    app.register_blueprint(routes_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(ws_bp)
    sock.init_app(app)

    @app.route("/")
    def index():
        from ai_notes.models import Task
        from sqlalchemy import asc

        status_f = request.args.get("status") or ""
        priority_f = request.args.get("priority") or ""
        q_text = request.args.get("q") or ""
        sort = request.args.get("sort") or "deadline"

        q = Task.query
        if status_f in {"pending", "in_progress", "done"}:
            q = q.filter(Task.status == status_f)
        if priority_f in {"low", "medium", "high", "urgent"}:
            q = q.filter(Task.priority == priority_f)
        if q_text:
            like = f"%{q_text}%"
            q = q.filter((Task.title.ilike(like)) | (Task.description.ilike(like)))

        if sort == "deadline":
            q = q.order_by(Task.deadline_utc.asc().nullslast())
        elif sort == "created_desc":
            q = q.order_by(Task.created_at.desc())
        elif sort == "title":
            q = q.order_by(asc(Task.title))
        elif sort == "priority":
            order_map = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
            # emulate priority order client-side in template; fallback server order by title
            q = q.order_by(asc(Task.title))
        else:
            q = q.order_by(Task.deadline_utc.asc().nullslast())

        tasks = q.all()

        # counts (unfiltered) for quick stats
        total = Task.query.count()
        pending_c = Task.query.filter(Task.status == "pending").count()
        prog_c = Task.query.filter(Task.status == "in_progress").count()
        done_c = Task.query.filter(Task.status == "done").count()

        return render_template(
            "index.html",
            tasks=tasks,
            total=total,
            pending_c=pending_c,
            prog_c=prog_c,
            done_c=done_c,
            status_f=status_f,
            priority_f=priority_f,
            q_text=q_text,
            sort=sort,
        )

    return app


app = create_app()

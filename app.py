import os
from dotenv import load_dotenv
from flask import Flask, render_template
from ai_notes.db import init_db, db
from ai_notes.scheduler import init_scheduler
from ai_notes.routes import bp as routes_bp
from ai_notes.api import bp as api_bp
from ai_notes.sockets.ai_ws import sock, bp as ws_bp


def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "ai_notes", "templates"))
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

        tasks = Task.query.order_by(Task.deadline_utc.asc().nullslast()).all()
        return render_template("index.html", tasks=tasks)

    return app


app = create_app()

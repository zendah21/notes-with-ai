from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    with app.app_context():
        from . import models  # noqa: F401

        db.create_all()
        # Lightweight SQLite migration: add description column if missing
        try:
            engine = db.engine
            # Verify table exists and column presence
            res = engine.execute(text("PRAGMA table_info(task)"))
            cols = [r[1] for r in res.fetchall()]
            if "description" not in cols:
                engine.execute(text("ALTER TABLE task ADD COLUMN description TEXT"))
        except Exception:
            # Best-effort; ignore if not SQLite or already applied
            pass

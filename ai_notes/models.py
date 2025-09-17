from datetime import datetime
from .db import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(32), default="pending")  # pending|in_progress|done
    priority = db.Column(db.String(16), default="medium")  # low|medium|high|urgent
    estimated_duration_minutes = db.Column(db.Integer, nullable=True)
    deadline_utc = db.Column(db.DateTime, nullable=True)
    notify_offsets_minutes = db.Column(db.String(255), nullable=True)  # CSV list
    tags = db.Column(db.String(255), nullable=True)  # CSV list of tags
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def notify_list(self):
        if not self.notify_offsets_minutes:
            return []
        try:
            return [int(x) for x in self.notify_offsets_minutes.split(",") if x]
        except Exception:
            return []

    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]

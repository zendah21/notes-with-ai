from __future__ import annotations
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError
from .hf_client import hf_zero_shot, hf_ner, hf_text2json
from ..models import Task
from ..db import db
from ..scheduler import on_task_changed
from ..utils.time import parse_natural_datetime, to_utc_iso


class TargetModel(BaseModel):
    by: str
    value: Any


class FieldsModel(BaseModel):
    priority: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    deadline_utc: Optional[str] = None
    notify_offsets_minutes: Optional[List[int]] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    title: Optional[str] = None


class ParsedAction(BaseModel):
    operation: str
    target: Optional[TargetModel] = None
    fields: FieldsModel = Field(default_factory=FieldsModel)
    notes: Optional[str] = None


PRIORITY_MAP = {
    "low": "low",
    "medium": "medium",
    "normal": "medium",
    "high": "high",
    "urgent": "urgent",
    "asap": "urgent",
    "today": "high",
}

INTENT_LABELS = ["create", "update", "delete", "complete", "reopen", "query"]


class AIRouter:
    def infer_intent(self, utterance: str) -> str:
        try:
            label, _ = hf_zero_shot(utterance, INTENT_LABELS)
            return label
        except Exception:
            # Fallback rule-of-thumb
            u = utterance.lower()
            if any(k in u for k in ["create", "new", "add"]):
                return "create"
            if any(k in u for k in ["done", "complete", "finished"]):
                return "complete"
            if any(k in u for k in ["reopen", "undo"]):
                return "reopen"
            if any(k in u for k in ["delete", "remove"]):
                return "delete"
            return "update"

    def resolve_target(self, utterance: str, user_id: str) -> Optional[TargetModel]:
        # Try to find quoted text (straight or smart quotes) as title
        m = re.search(r"[\"'“”‘’]([^\"'“”‘’]+)[\"'“”‘’]", utterance)
        title = m.group(1) if m else None
        if title:
            # fuzzy match titles by simple substring
            tasks = Task.query.all()
            best = None
            for t in tasks:
                if title.lower() in t.title.lower():
                    best = t
                    break
            if best:
                return TargetModel(by="id", value=best.id)
            return TargetModel(by="title", value=title)
        return None

    def _extract_duration(self, utterance: str) -> Optional[int]:
        m = re.search(r"\b(\d+)\s*(min|m|minutes|hour|h|hours)\b", utterance, re.I)
        if not m:
            return None
        n = int(m.group(1))
        unit = m.group(2).lower()
        if unit.startswith("h"):
            return n * 60
        return n

    def _extract_priority(self, utterance: str) -> Optional[str]:
        for k, v in PRIORITY_MAP.items():
            if re.search(rf"\b{k}\b", utterance, re.I):
                return v
        return None

    def _extract_notifications(self, utterance: str) -> Optional[List[int]]:
        mins: List[int] = []
        # Find first alert-like keyword, accept plural/synonyms
        kw = re.search(r"\b(alerts?|notif(y|ies|ication|ications)|remind(ers?)?|alarms?)\b", utterance, re.I)
        if kw:
            start = kw.start()
            # Capture all durations after the keyword (supports 'and', ',', '/'), e.g., "alerts 12h and 1h"
            for m in re.finditer(r"(\d+)\s*(h|hour|hours|m|min|minute)s?", utterance[start:], re.I):
                n = int(m.group(1))
                unit = (m.group(2) or "m").lower()
                mins.append(n * 60 if unit.startswith("h") else n)
        # pattern B: "12h|30m before|prior"
        for m in re.finditer(r"(\d+)\s*(h|hour|hours|m|min|minute)s?\s*(before|prior)\b", utterance, re.I):
            n = int(m.group(1))
            unit = (m.group(2) or "m").lower()
            mins.append(n * 60 if unit.startswith("h") else n)
        if mins:
            mins = sorted({int(x) for x in mins})
            return mins
        return None

    def _extract_deadline(self, utterance: str, tz: str) -> Optional[str]:
        # try dateutil first; rely on words like tomorrow, Friday 9:30
        try:
            dt = parse_natural_datetime(utterance, default_tz=tz)
            return to_utc_iso(dt)
        except Exception:
            return None

    def extract_fields(self, utterance: str, tz: str) -> Dict[str, Any]:
        fields: Dict[str, Any] = {}
        # Rules first
        dur = self._extract_duration(utterance)
        if dur is not None:
            fields["estimated_duration_minutes"] = dur
        pr = self._extract_priority(utterance)
        if pr is not None:
            fields["priority"] = pr
        # status
        if re.search(r"\b(in\s*progress|ongoing)\b", utterance, re.I):
            fields["status"] = "in_progress"
        nt = self._extract_notifications(utterance)
        if nt is not None:
            fields["notify_offsets_minutes"] = nt
        # Ambiguity guard: if the text contains 'maybe' or 'or' between days, skip setting a deadline
        if not re.search(r"\bmaybe\b|\b(mon|tue|wed|thu|fri|sat|sun)\b\s*or\s*\b(mon|tue|wed|thu|fri|sat|sun)\b", utterance, re.I):
            # handle 'before Sunday' as end-of-day Sunday
            m = re.search(r"before\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", utterance, re.I)
            if m:
                try:
                    dow = m.group(1)
                    from dateutil import tz as dzt
                    local_dt = parse_natural_datetime(dow, default_tz=tz)
                    # set to 23:59 local
                    local_dt = local_dt.replace(hour=23, minute=59, second=0, microsecond=0)
                    fields["deadline_utc"] = to_utc_iso(local_dt)
                except Exception:
                    pass
            else:
                dl = self._extract_deadline(utterance, tz)
                if dl is not None:
                    fields["deadline_utc"] = dl

        # NER assist: find tags from ORG/MISC; also derive description from leftovers
        try:
            ents = hf_ner(utterance)
            tags = sorted({e.get("entity_group") for e in ents if e.get("entity_group") in {"ORG", "MISC"}})
            if tags:
                fields["tags"] = tags
        except Exception:
            pass

        # Lightweight description: remaining text after removing time/duration/notify keywords
        try:
            rem = utterance
            rem = re.sub(r"\b(alerts?|notify|remind|alarm)s?\b[\s\S]*$", "", rem, flags=re.I)
            rem = re.sub(r"\b(\d+)\s*(h|hour|hours|m|min|minute)s?(\s*(before|prior))?\b", "", rem, flags=re.I)
            rem = re.sub(r"\b(tomorrow|today|tonight|this\s+afternoon|this\s+evening|next\s+\w+|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}:\d{2}|\d{1,2}\s*(am|pm))\b", "", rem, flags=re.I)
            rem = re.sub(r"\s+", " ", rem).strip(" .,-")
            if rem and len(rem) > 0:
                fields.setdefault("description", rem)
        except Exception:
            pass

        return fields

    def _t2t_schema(self, utterance: str, tz: str) -> Dict[str, Any]:
        sys = (
            "SYSTEM: Convert the instruction to this JSON schema (no prose):"
            " {operation, target:{by,value}, fields:{priority,estimated_duration_minutes,deadline_utc,notify_offsets_minutes,status,tags,description,title}}"
            f" TIMEZONE={tz}; All final times must be UTC ISO8601.\n"
        )
        user = f'USER: "{utterance}"\n'
        return hf_text2json(sys + user) or {}

    def build_action(self, utterance: str, tz: str, user_id: str, default_title: Optional[str] = None) -> Dict[str, Any]:
        intent = self.infer_intent(utterance)
        target = self.resolve_target(utterance, user_id)
        fields = self.extract_fields(utterance, tz)

        # If poor signal, ask T2T to help
        t2t = {}
        try:
            if not fields or intent in {"create", "update"}:
                t2t = self._t2t_schema(utterance, tz)
        except Exception:
            t2t = {}

        # Merge fields (rules override t2t on conflict)
        if t2t.get("fields"):
            for k, v in t2t["fields"].items():
                fields.setdefault(k, v)
        if not target and t2t.get("target"):
            try:
                target = TargetModel(**t2t["target"])  # type: ignore
            except Exception:
                target = None
        if not intent and t2t.get("operation"):
            intent = t2t.get("operation")

        # Default create if no target & intent ambiguous
        if not target and intent not in {"create", "query"}:
            intent = "create"
        # If creating and no target, use provided default title as best effort
        if (not target) and intent == "create" and default_title:
            target = TargetModel(by="title", value=default_title)

        # Pydantic validation and shaping
        try:
            model = ParsedAction(
                operation=intent,
                target=target,
                fields=FieldsModel(**fields),
                notes=(
                    "Rule-first parse with HF assist; times normalized to UTC"
                ),
            )
        except ValidationError as e:
            model = ParsedAction(operation=intent, fields=FieldsModel(), notes=f"validation_error: {e}")

        return model.model_dump(exclude_none=False)

    # Apply to DB helpers (used by WebSocket flow)
    def apply_action(self, action: Dict[str, Any]) -> Task:
        op = action.get("operation")
        target = action.get("target") or {}
        fields = action.get("fields") or {}

        def _apply_fields(t: Task):
            if "priority" in fields and fields["priority"]:
                t.priority = fields["priority"]
            if "estimated_duration_minutes" in fields and fields["estimated_duration_minutes"] is not None:
                t.estimated_duration_minutes = int(fields["estimated_duration_minutes"])
            if "deadline_utc" in fields and fields["deadline_utc"]:
                # parse as ISO
                from dateutil import parser

                try:
                    t.deadline_utc = parser.isoparse(fields["deadline_utc"]).replace(tzinfo=None)
                except Exception:
                    t.deadline_utc = None
            if "notify_offsets_minutes" in fields and fields["notify_offsets_minutes"] is not None:
                t.notify_offsets_minutes = ",".join(str(x) for x in fields["notify_offsets_minutes"])
            if "tags" in fields and fields["tags"] is not None:
                t.tags = ",".join(fields["tags"]) if isinstance(fields["tags"], list) else str(fields["tags"])
            if "status" in fields and fields["status"]:
                t.status = fields["status"]
            if "description" in fields and fields["description"]:
                t.description = str(fields["description"]).strip() or None
            if "title" in fields and fields["title"]:
                v = str(fields["title"]).strip()
                if v:
                    t.title = v

        if op == "create":
            title = (target or {}).get("value") or "New Task"
            t = Task(title=str(title))
            db.session.add(t)
            db.session.flush()
            _apply_fields(t)
            db.session.commit()
            on_task_changed(t)
            return t
        else:
            # resolve existing
            t: Optional[Task] = None
            if target.get("by") == "id":
                t = Task.query.get(target.get("value"))
            elif target.get("by") == "title" and target.get("value"):
                v = str(target.get("value")).lower()
                t = Task.query.filter(Task.title.ilike(f"%{v}%")).first()
            if not t:
                # fall back to create on updates when no target
                if op in {"update"}:
                    return self.apply_action({"operation": "create", "target": target, "fields": fields})
                # else create a basic task to proceed
                t = Task(title=str((target or {}).get("value") or "Task"))
                db.session.add(t)
                db.session.flush()

            if op == "update":
                _apply_fields(t)
            elif op == "complete":
                t.status = "done"
            elif op == "reopen":
                t.status = "pending"
            elif op == "delete":
                db.session.delete(t)
                db.session.commit()
                return t

            db.session.commit()
            on_task_changed(t)
            return t

from datetime import datetime
from dateutil import parser, tz


def parse_natural_datetime(text: str, default_tz: str = "Asia/Kuwait"):
    # Uses dateutil for simple expressions; callers must handle ambiguity
    local = tz.gettz(default_tz)
    dt = parser.parse(text, fuzzy=True, default=datetime.now(local))
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=local)
    return dt


def to_utc_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz.UTC)
    return dt.astimezone(tz.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


from ai_notes.utils.time import parse_natural_datetime, to_utc_iso


def test_parse_to_utc_iso():
    dt = parse_natural_datetime("tomorrow 10am", default_tz="Asia/Kuwait")
    iso = to_utc_iso(dt)
    assert iso.endswith("Z")


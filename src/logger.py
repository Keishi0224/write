from datetime import datetime, timezone
from .common import ROOT, atomic_json, read_json

def record(event, detail):
    path = ROOT / "logs/events.json"
    events = read_json(path, [])
    events.append({"at": datetime.now(timezone.utc).isoformat(), "event": event, "detail": str(detail)[:1500]})
    atomic_json(path, events[-200:])

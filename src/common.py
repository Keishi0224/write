import json
import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]

def today():
    return datetime.now(ZoneInfo("Asia/Tokyo")).date()

def read_json(path, default=None):
    if not path.exists() and default is not None:
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)

def settings():
    # JSON is a YAML 1.2 subset: no external YAML dependency needed.
    return read_json(ROOT / "config/settings.yaml")

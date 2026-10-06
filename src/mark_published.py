import os
from datetime import datetime, timezone
from .common import ROOT, read_json, atomic_json, settings
from .cost_guard import check

if __name__ == "__main__":
    check(settings())
    if os.environ.get("DEPLOYMENT_SUCCEEDED") != "true":
        raise SystemExit("公開完了が確認できません。")
    posts = read_json(ROOT / "data/published.json", [])
    for post in posts:
        if post["status"] == "prepared":
            post.update(status="published", published_at=datetime.now(timezone.utc).isoformat())
    atomic_json(ROOT / "data/published.json", posts)

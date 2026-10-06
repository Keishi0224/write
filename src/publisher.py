import json
import os
from .common import ROOT, atomic_json

def publish(article, history):
    path = ROOT / "posts" / (article["slug"] + ".md")
    if path.exists():
        raise ValueError("既存の記事は上書きしません。")
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = {k: v for k, v in article.items() if k != "body"}
    content = "---\n" + json.dumps(meta, ensure_ascii=False, indent=2) + "\n---\n\n" + article["body"] + "\n"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
    entry = {k: article[k] for k in ("title", "slug", "topic_id", "category", "sources", "body_hash")}
    entry.update({"prepared_at": article["date"], "published_at": None, "status": "prepared"})
    try:
        atomic_json(ROOT / "data/published.json", history + [entry])
    except Exception:
        path.unlink()
        raise
    return path

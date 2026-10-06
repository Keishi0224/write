import hashlib
from .common import today

def generate(topic, sources):
    # The prose is independently authored and reviewed in the editorial queue.
    # Research verifies source availability; it is NOT an AI factuality assessment.
    sections = topic["sections"]
    body = topic["intro"] + "\n\n" + "\n\n".join("## " + s["heading"] + "\n\n" + s["body"] for s in sections)
    body += "\n\n## 今日のひとつ\n\n" + topic["takeaway"]
    return {"title": topic["title"], "description": topic["description"], "slug": topic["slug"], "topic_id": topic["topic_id"], "date": today().isoformat(), "category": topic["category"], "tags": topic["tags"], "sources": sources, "generation_mode": "editorial_templates", "reviewed": topic["reviewed"], "body_hash": hashlib.sha256(body.encode()).hexdigest(), "body": body}

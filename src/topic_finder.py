from .duplicate_checker import is_duplicate

def find_topic(topics, history, config):
    # Curated queue only: an unknown topic never becomes an invented article.
    candidates = [t for t in topics if t.get("reviewed") is True and t["category"] in config["allowed_categories"] and not is_duplicate(t, history)]
    return sorted(candidates, key=lambda t: (-t.get("priority", 0), t["topic_id"]))[0] if candidates else None

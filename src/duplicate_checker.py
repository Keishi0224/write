import re
from difflib import SequenceMatcher

def normalized(text):
    return re.sub(r"[^\w]", "", text).casefold()

def is_duplicate(topic, history):
    for post in history:
        if topic["slug"] == post["slug"] or topic.get("topic_id") == post.get("topic_id"):
            return True
        if SequenceMatcher(None, normalized(topic["title"]), normalized(post["title"])).ratio() >= 0.85:
            return True
    return False

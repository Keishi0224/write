import re
from .duplicate_checker import is_duplicate
from .researcher import safe_url

def validate(article, history, config):
    for key in ("title", "description", "date", "category", "body", "sources"):
        if not article.get(key):
            raise ValueError("記事の必須項目がありません: " + key)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", article["slug"]):
        raise ValueError("記事のURLが不正です。")
    if not article.get("reviewed") or article["generation_mode"] != "editorial_templates":
        raise ValueError("未確認の原稿は公開できません。")
    if len(article["body"]) < 300 or len(article["title"]) > 70 or len(article["description"]) > 180:
        raise ValueError("記事の長さを確認してください。")
    if article["category"] not in config["allowed_categories"]:
        raise ValueError("自動公開対象外のカテゴリです。")
    if any(term in article["title"] + article["body"] for term in config["blocked_terms"]):
        raise ValueError("自動公開対象外の表現があります。")
    if is_duplicate(article, history) or any(p.get("body_hash") == article["body_hash"] for p in history):
        raise ValueError("重複記事です。")
    for source in article["sources"]:
        safe_url(source["url"], config["allowed_hosts"])

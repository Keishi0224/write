import argparse
import sys
from .common import ROOT, read_json, settings, today
from .cost_guard import check
from .topic_finder import find_topic
from .researcher import research
from .article_generator import generate
from .validator import validate
from .publisher import publish
from .logger import record

def run(local=False):
    config = settings()
    check(config, local)
    history = read_json(ROOT / "data/published.json", [])
    if sum(p.get("prepared_at") == today().isoformat() for p in history) >= config["max_posts_per_day"]:
        record("skipped", "本日の記事作成上限に達しました。")
        return
    topic = find_topic(read_json(ROOT / "data/topics.json"), history, config)
    if topic is None:
        record("queue_empty", "確認済み記事候補がありません。追加の編集が必要です。")
        return
    sources = research(topic, config)
    article = generate(topic, sources)
    validate(article, history, config)
    path = publish(article, history)
    record("prepared", path.name)
    print("Prepared:", path.name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="Local preparation only, no deployment")
    args = parser.parse_args()
    try:
        run(args.local)
    except Exception as exc:
        record("stopped", str(exc))
        print("Stopped:", exc, file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

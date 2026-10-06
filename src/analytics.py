import argparse
from urllib.parse import urlsplit
from .common import ROOT, read_json, atomic_json, settings

def analyze(input_path):
    # Accept a real, aggregated GSC export. Never synthesize metrics.
    raw = read_json(input_path)
    if not isinstance(raw, dict) or not isinstance(raw.get('rows'), list):
        raise ValueError('rowsを持つJSONが必要です。')
    base = settings()['base_url'].rstrip('/')
    results = []
    for row in raw['rows']:
        page = row.get('page', '')
        if not page.startswith(base + '/posts/') or not page.endswith('.html'):
            continue
        if urlsplit(page).query or urlsplit(page).fragment:
            continue
        clicks = float(row['clicks'])
        impressions = float(row['impressions'])
        position = float(row['position'])
        if clicks < 0 or impressions < clicks or position < 1:
            raise ValueError('検索データの値が不正です。')
        ctr = clicks / impressions if impressions else 0
        action = 'タイトルと説明文を確認' if impressions >= 100 and ctr < .02 else '本文と検索意図を確認' if impressions >= 100 and position > 10 else 'データを蓄積'
        results.append({'page': page, 'clicks': clicks, 'impressions': impressions, 'ctr': ctr, 'position': position, 'suggested_action': action})
    results.sort(key=lambda r: (-r['impressions'], r['ctr']))
    atomic_json(ROOT/'data/analytics.json', {'connected': True, 'source': 'GSC export', 'rows': results})
    # Recommendations only. A low CTR is not enough evidence to rewrite a fact.
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=__import__('pathlib').Path)
    args = parser.parse_args()
    print(analyze(args.input))

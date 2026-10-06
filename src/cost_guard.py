import os
from datetime import date
from .common import today

def check(config, local=False):
    policy = config["cost_policy"]
    age = (today() - date.fromisoformat(policy["verified_on"])).days
    if age < 0 or age > policy["valid_days"]:
        raise ValueError("無料条件の確認期限切れ。公式料金を再確認するまで生成・公開を停止します。")
    if policy["paid_apis_enabled"] or config["generation_mode"] != "editorial_templates":
        raise ValueError("追加料金が不要と検証された記事生成方式だけを許可します。")
    if policy["hosting"] != "github_pages" or policy["runner"] != "ubuntu-latest":
        raise ValueError("未確認の公開先または実行環境です。")
    if not local and (os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("REPOSITORY_VISIBILITY") != "public"):
        raise ValueError("自動公開はGitHubの公開リポジトリに限定します。")

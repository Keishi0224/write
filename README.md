# デジタル手帖 — 無料の自動記事サイト

日本語のデジタル活用・Web基礎メディア。GitHub Pages + 公開リポジトリの標準GitHub Actions + Python標準ライブラリのみを使います。有料API、広告、外部画像、追加パッケージは使いません。

公開予定URL: https://keishi0224.github.io/write/

## 初版でできること

- 記事一覧、記事詳細、目次、参考情報、編集方針、スマートフォン対応。
- タイトル、description、canonical、BlogPosting構造化データ、sitemap、robots、RSS。
- 毎日08:17ごろ（日本時間、GitHubの実行遅延あり）、未掲載の確認済み候補を選び、公式出典を取得確認して1日最大1記事を作成。
- 重複、必須項目、対象カテゴリ、禁止表現、出典の取得失敗をチェック。失敗時は公開しない。
- 実際のPages公開が成功した後にのみ履歴をpublishedに更新。準備中はprepared。
- エラーと処理履歴を logs/events.json に保存。秘密情報は保存しない。

## 重要な範囲と制約

初版は無料AIの完全無人実行を利用しません。8件の独自編集原稿をキューに用意し、確認済み原稿からルールで記事を組み立てます。公開時点の初期記事以外を1日1件ずつ処理します。候補が尽きたらqueue_emptyとして停止し、タイトルを変えた類似記事を量産しません。無限に新しいテーマを調査・執筆する仕組みではありません。

出典ページの取得と想定語の確認は、内容の正確さの自動保証ではありません。新規原稿と重要な仕様変更は内容の確認が必要です。自動的な事実判定や自動リライトは実装していません。

完全無料の条件は公開リポジトリ、標準ubuntu-latest、GitHub Pagesです。私有リポジトリではワークフローの実行前に停止します。30日ごとに公式の無料条件を確認し、config/settings.yaml の cost_policy.verified_on を更新してください。期限切れで生成・公開を止めます。料金変更の確実な自動検知はできないため、料金に不確実性があれば停止してください。無料サービス自体の仕様変更は制御できません。

## GitHubでの初期設定

1. 公開リポジトリを使う（初版では指定されたwrite）。
2. Settings → Pages → Source をGitHub Actionsにする。
3. この一式をmainへ保存するとPublish Pagesが公開する。
4. 次の日からDaily articleが候補を処理する。手動実行はActions → Daily article → Run workflow。

定期ワークフローは長期間リポジトリが非アクティブな場合にGitHubが停止することがあります。時刻どおりの実行は保証されません。失敗はActionsとlogs/events.jsonで確認してください。

## 手元での確認

Python 3.11以上を使います。外部のパッケージをインストールする必要はありません。

```text
python -m unittest discover -s tests -v
python -m src.main --local
python -m src.build
python -m http.server 8765 --directory dist --bind 127.0.0.1
```

--localは記事ファイルの準備だけです。インターネット公開は行いません。config/settings.yaml は依存パッケージを不要にするためJSON形式（YAML 1.2のサブセット）です。

posts/の原稿はJSON front matterの後にMarkdown本文を置きます。対応記法は段落、##の見出し、-の箇条書き、バッククォートのインラインコード。その他のMarkdown記法は初版では扱いません。

## 記事候補の追加

data/topics.json に topic_id、slug、title、description、category、tags、sources、intro、sections、takeaway を持つ独自原稿を追加します。sourcesには公式URLとexpected_termsを指定。記事内容と出典の対応を確認してから reviewed を true にします。ここへの未確認原稿の投入を自動化しないでください。

## GSC Wizard / WPWriter

作成時点では両アプリに接続済みサイトがありません。WordPressを新規契約せず、仕様書のGitHub Pagesを利用します。WPWriterはWordPress用なので、この静的サイトへの投稿経路には使用しません。

検索改善は未接続です。公開後にSearch ConsoleでURLプレフィックスの所有権を確認し、GSC Wizardへ接続する必要があります。確認用HTMLファイルがある場合はdistへコピーする処理を追加します。接続前の数値は作りません。

集計済み実測データをJSONで取得できたら `python -m src.analytics path/to/export.json` で優先確認ページを算出します。入力形式は `{"rows":[{"page":"https://keishi0224.github.io/write/posts/example.html","clicks":1,"impressions":100,"position":12}]}`。検索語やユーザー識別子は含めないでください。改善提案のみで自動リライトしません。GSC Wizardの認証情報をGitHubへ持ち出さず、定期分析は接続後に検討します。

## 無料条件の公式資料

- https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows

添付の元仕様は PROJECT_SPEC.md に保存しています。Libraryの原本は変更していません。

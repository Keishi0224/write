import argparse
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape
from .common import ROOT, settings

def esc(value):
    return html.escape(str(value), quote=True)

def read_post(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("JSON front matterが必要です: " + path.name)
    _, metadata, body = text.split("---\n", 2)
    article = json.loads(metadata)
    article["body"] = body.strip()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", article["slug"]):
        raise ValueError("Invalid slug")
    return article

def inline(text):
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", esc(text))

def markdown(text):
    output, toc = [], []
    for block in text.split("\n\n"):
        if block.startswith("## "):
            title = block[3:].strip()
            anchor = "section-" + str(len(toc) + 1)
            toc.append((anchor, title))
            output.append(f'<h2 id="{anchor}">{esc(title)}</h2>')
        elif all(line.startswith("- ") for line in block.splitlines()):
            output.append("<ul>" + "".join("<li>" + inline(line[2:]) + "</li>" for line in block.splitlines()) + "</ul>")
        else:
            output.append("<p>" + inline(block).replace("\n", "<br>") + "</p>")
    return "".join(output), toc

def illustration(index=0):
    if index % 3 == 0:
        return '<svg viewBox="0 0 400 250" aria-hidden="true"><circle cx="302" cy="60" r="34" fill="#b34d2b"/><path d="M45 213h310" stroke="#22332f" stroke-width="3"/><rect x="70" y="47" width="205" height="142" rx="8" fill="#faf8f2" stroke="#22332f" stroke-width="3"/><path d="M70  seventy"/><path d="M70 76h205" stroke="#22332f" stroke-width="2"/><circle cx="85" cy="62" r="3" fill="#b34d2b"/><circle cx="98" cy="62" r="3" fill="#63716a"/><path d="m116 111-16 16 16 16m83-32 16 16-16 16m-43-39-14 49" stroke="#22332f" stroke-width="4" fill="none"/><path d="m290 150 45 45-21 3-11 20z" fill="#b34d2b" stroke="#22332f" stroke-width="2"/><path d="M155 190v22m35-22v22" stroke="#22332f" stroke-width="3"/></svg>'.replace('<path d="M70  seventy"/>', '')
    if index % 3 == 1:
        return '<svg viewBox="0 0 400 250" aria-hidden="true"><circle cx="295" cy="72" r="50" fill="#d6a16e"/><path d="M70 199h266" stroke="#22332f" stroke-width="3"/><rect x="100" y="45" width="145" height="155" rx="3" fill="#faf8f2" stroke="#22332f" stroke-width="3" transform="rotate(-8 170 120)"/><rect x="146" y="70" width="145" height="130" rx="3" fill="#faf8f2" stroke="#22332f" stroke-width="3"/><path d="M164 101h102m-102 22h78m-78 22h92m-92 22h50" stroke="#63716a" stroke-width="3"/><rect x="79" y="129" width="55" height="71" fill="#b34d2b" stroke="#22332f" stroke-width="2"/></svg>'
    return '<svg viewBox="0 0 400 250" aria-hidden="true"><circle cx="195" cy="124" r="84" fill="#faf8f2" stroke="#22332f" stroke-width="3"/><ellipse cx="195" cy="124" rx="37" ry="84" fill="none" stroke="#22332f" stroke-width="2"/><path d="M111 124h168m-156-40h142m-142 80h142" stroke="#22332f" stroke-width="2"/><circle cx="270" cy="61" r="32" fill="#b34d2b"/><path d="m257 62 9 9 18-21" stroke="#faf8f2" stroke-width="4" fill="none"/><path d="M75 217h242" stroke="#22332f" stroke-width="3"/></svg>'

LOGO = '<svg viewBox="0 0 36 36" aria-hidden="true"><rect x="2" y="2" width="32" height="32" rx="5" fill="#22332f"/><path d="M11 9h15v19H11z" fill="none" stroke="#faf8f2" stroke-width="2"/><path d="M8 12h6m-6 6h6m-6 6h6m5-10h5m-5 5h5" stroke="#d6a16e" stroke-width="2"/></svg>'

def shell(title, description, content, prefix, config, canonical=None, schema=None):
    full_title = title if title == config["site_title"] else title + ' | ' + config["site_title"]
    # Public ownership verification tag for the user-approved Search Console property.
    tags = '<meta name="google-site-verification" content="mkg372-sq2Tb7xuXVzspmxaZcBKQrTX486xtARTeyk4">'
    if canonical:
        tags += f'<link rel="canonical" href="{esc(canonical)}"><meta property="og:url" content="{esc(canonical)}">'
    if schema:
        tags += '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    favicon = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"%3E%3Crect width="36" height="36" rx="5" fill="%2322332f"/%3E%3Cpath d="M11 9h15v19H11z" fill="none" stroke="%23faf8f2" stroke-width="2"/%3E%3C/svg%3E'
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(full_title)}</title><meta name="description" content="{esc(description)}"><meta property="og:title" content="{esc(full_title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="{'article' if schema else 'website'}"><link rel="icon" href='{favicon}'><link rel="stylesheet" href="{prefix}assets/style.css">{tags}</head><body><a class="skip" href="#content">本文へ移動</a><header><a class="brand" href="{prefix}index.html">{LOGO}デジタル手帖</a><nav aria-label="メイン"><a href="{prefix}index.html#articles">記事一覧</a><a href="{prefix}about.html">この手帖について</a></nav></header><main id="content">{content}</main><footer><span>デジタル手帖 · Webの基礎を、ひとつずつ。</span><a href="{prefix}about.html#privacy">プライバシーと編集方針</a></footer></body></html>'''

def meta(article):
    minutes = max(2, round(len(article["body"]) / 500))
    return f'<div class="meta"><time datetime="{esc(article["date"])}">{esc(article["date"].replace("-", "."))}</time><span>約{minutes}分で読めます</span></div>'

def build(base_url=None, output=None):
    config = settings()
    base = (base_url if base_url is not None else config["base_url"]).rstrip('/')
    if base and (urlsplit(base).scheme != 'https' or urlsplit(base).query or urlsplit(base).fragment):
        raise ValueError('Public base URL must be HTTPS')
    output = Path(output) if output else ROOT / 'dist'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'assets').mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'assets/style.css', output / 'assets/style.css')
    articles = sorted((read_post(p) for p in (ROOT / 'posts').glob('*.md')), key=lambda p: (p['date'], p['slug']), reverse=True)
    for article in articles:
        body, toc = markdown(article['body'])
        slug = article['slug']
        url = base + '/posts/' + slug + '.html' if base else None
        schema = {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': article['title'], 'description': article['description'], 'datePublished': article['date'], 'author': {'@type': 'Organization', 'name': config['site_title']}, 'inLanguage': 'ja'}
        if url:
            schema['mainEntityOfPage'] = url
        source_links = ''.join(f'<li><a href="{esc(s["url"])}" rel="noopener noreferrer">{esc(s["title"])}</a></li>' for s in article['sources'])
        sources = '<section class="sources"><h2>参考情報</h2><ul>' + source_links + '</ul><p class="tiny">独自の編集原稿をもとに作成。出典の取得確認と記事内容の確認は別の工程です。</p></section>'
        side = '<aside aria-label="目次"><h2>このページの内容</h2>' + ''.join(f'<a href="#{a}">{esc(t)}</a>' for a, t in toc) + '</aside>'
        content = f'<div class="crumb"><a href="../index.html">ホーム</a> / {esc(article["category"])}</div><div class="article-head"><span class="category">{esc(article["category"])}</span><h1>{esc(article["title"])}</h1><p class="summary">{esc(article["description"])}</p>{meta(article)}</div><div class="article-layout"><article class="prose">{body}{sources}<a class="read" href="../index.html#articles">記事一覧に戻る <span>↗</span></a></article>{side}</div>'
        (output / 'posts').mkdir(exist_ok=True)
        (output / 'posts' / (slug + '.html')).write_text(shell(article['title'], article['description'], content, '../', config, url, schema), encoding='utf-8')
    content = '<section class="intro"><div><div class="eyebrow">THE DIGITAL NOTEBOOK</div><h1>知ることから、<br>デジタルはもっと身近に。</h1><p>Webの小さな疑問をほどく、やさしい読みもの。</p></div><p class="intro-note">難しい言葉は、ひとつずつ。<br>読み終えたら、小さな一歩を。</p></section>'
    if articles:
        a = articles[0]
        link = 'posts/' + a['slug'] + '.html'
        content += f'<section class="feature"><a href="{link}" class="art" aria-label="{esc(a["title"])}">{illustration()}</a><div><span class="eyebrow">PICK UP / 今日の読みもの</span><h2><a href="{link}">{esc(a["title"])}</a></h2><p class="summary">{esc(a["description"])}</p>{meta(a)}<a class="read" href="{link}">記事を読む <span>↗</span></a></div></section>'
    else:
        content += '<p class="empty">最初の記事を準備しています。</p>'
    content += '<section id="articles"><div class="section-title"><h2>すべての読みもの</h2><span>THE NOTES · ' + str(len(articles)).zfill(2) + '</span></div><div class="grid">'
    for i, a in enumerate(articles):
        link = 'posts/' + a['slug'] + '.html'
        cls = ('', 'warm', 'blue')[i % 3]
        content += f'<article class="card"><a class="art {cls}" href="{link}" aria-label="{esc(a["title"])}">{illustration(i)}</a><span class="category">{esc(a["category"])}</span><h3><a href="{link}">{esc(a["title"])}</a></h3><p class="summary">{esc(a["description"])}</p>{meta(a)}</article>'
    content += '</div></section><section class="about-strip"><h2>小さく学ぶ。<br>少しずつ、使える。</h2><p>この手帖は、Webの基礎やサイトづくりを自分のペースで学ぶための読みものです。公式の情報を参考に、身近な例と、今日から試せる小さな工夫をお届けします。<br><a class="read" href="about.html">この手帖について ↗</a></p></section>'
    (output / 'index.html').write_text(shell(config['site_title'], config['site_description'], content, '', config, base + '/' if base else None), encoding='utf-8')
    about = '<article class="policy"><div class="eyebrow">ABOUT THE NOTEBOOK</div><h1>この手帖について</h1><p>デジタル手帖は、Webの仕組みやサイトづくりを学ぶ人のための日本語メディアです。ひとつの記事でひとつの疑問をほどき、試せる行動につなげます。</p><h2>記事のつくり方</h2><p>初版は、独自に用意した編集原稿をもとに、記事ファイルとページを自動生成します。公式情報の取得、重複、必須項目のチェックを行います。機械的なチェックだけで事実の正確さが保証されるとは考えていません。</p><h2>扱うテーマ</h2><p>Webの基礎、サイトづくり、情報整理を扱います。医療・法律・金融の助言は自動公開対象に含めません。記事候補や出典に問題があれば、公開を止めます。</p><h2>出典と画像</h2><p>記事には参考情報へのリンクを添えます。他サイトの本文や画像を転載しません。このサイトのイラストは独自に制作しています。</p><h2 id="privacy">プライバシー</h2><p>このサイトでは、独自のアクセス解析、広告、入力フォーム、追跡Cookieを設置していません。配信元のGitHubがサービス提供のために扱うデータについては、GitHubのプライバシー声明をご確認ください。</p><p><a class="read" href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHubのプライバシー声明 ↗</a></p><h2>更新について</h2><p>確認済みの候補から1日最大1記事を作成します。新しい候補がないときは更新しません。料金の無料条件は定期的に再確認し、未確認の有料サービスへ自動的に切り替えません。</p></article>'
    (output / 'about.html').write_text(shell('この手帖について', 'デジタル手帖の編集方針、出典、プライバシーについて。', about, '', config, base + '/about.html' if base else None), encoding='utf-8')
    (output / '404.html').write_text(shell('ページが見つかりません', '記事一覧からお探しください。', '<div class="policy"><h1>ページが見つかりません</h1><a class="read" href="'+ esc(base + '/' if base else './index.html') +'">記事一覧へ ↗</a></div>', base + '/' if base else '', config), encoding='utf-8')
    (output / '.nojekyll').write_text('', encoding='utf-8')
    if base:
        urls = [base + '/', base + '/about.html'] + [base + '/posts/' + a['slug'] + '.html' for a in articles]
        sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + xml_escape(u) + '</loc></url>' for u in urls) + '</urlset>'
        (output / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
        (output / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + base + '/sitemap.xml\n', encoding='utf-8')
        feed = '<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>デジタル手帖</title><link>' + xml_escape(base) + '</link><description>' + xml_escape(config['site_description']) + '</description>'
        feed += ''.join('<item><title>' + xml_escape(a['title']) + '</title><link>' + xml_escape(base + '/posts/' + a['slug'] + '.html') + '</link><guid>' + xml_escape(base + '/posts/' + a['slug'] + '.html') + '</guid><description>' + xml_escape(a['description']) + '</description></item>' for a in articles)
        (output / 'feed.xml').write_text(feed + '</channel></rss>', encoding='utf-8')
    print('Built', len(articles), 'articles:', output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url')
    args = parser.parse_args()
    build(args.base_url)

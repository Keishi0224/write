import hashlib
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlsplit

def safe_url(url, allowed_hosts):
    p = urlsplit(url)
    if p.scheme != "https" or p.hostname not in allowed_hosts or p.username or p.password or p.port not in (None, 443):
        raise ValueError("許可していない出典URLです。")
    return url

class RedirectGuard(HTTPRedirectHandler):
    def __init__(self, hosts):
        self.hosts = hosts
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        safe_url(newurl, self.hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def research(topic, config):
    results = []
    opener = build_opener(RedirectGuard(config["allowed_hosts"]))
    for source in topic["sources"]:
        url = safe_url(source["url"], config["allowed_hosts"])
        request = Request(url, headers={"User-Agent": "DigitalTecho/1.0 (source availability check)"})
        with opener.open(request, timeout=20) as response:
            if response.status != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                raise ValueError("出典を読み取れません。")
            content = response.read(2_000_001)
            if len(content) > 2_000_000:
                raise ValueError("出典の容量上限を超えました。")
            text = content.decode("utf-8", errors="replace").casefold()
            if not any(term.casefold() in text for term in source["expected_terms"]):
                raise ValueError("出典の内容が想定と異なります。確認が必要です。")
            results.append({"title": source["title"], "url": url, "sha256": hashlib.sha256(content).hexdigest()})
    if not results:
        raise ValueError("出典がありません。")
    return results

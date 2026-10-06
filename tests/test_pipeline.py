import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import timedelta
from src.common import ROOT, settings, read_json, today
from src.cost_guard import check
from src.article_generator import generate
from src.duplicate_checker import is_duplicate
from src.validator import validate
from src.researcher import safe_url, research
from src.publisher import publish
from src.build import build, markdown
from src.topic_finder import find_topic

class Safeguards(unittest.TestCase):
    def setUp(self):
        self.config = settings()
        # Tests model a freshly verified policy, independent of the live expiry.
        self.config['cost_policy']['verified_on'] = today().isoformat()
        self.topic = read_json(ROOT/'data/topics.json')[0]
        sources = [{'title':s['title'], 'url':s['url'], 'sha256':'test-only'} for s in self.topic['sources']]
        self.article = generate(self.topic, sources)

    def test_private_repository_and_paid_mode_are_blocked(self):
        with patch.dict(os.environ, {'GITHUB_ACTIONS':'true', 'REPOSITORY_VISIBILITY':'private'}):
            with self.assertRaises(ValueError):
                check(self.config)
        self.config['cost_policy']['paid_apis_enabled'] = True
        with self.assertRaises(ValueError):
            check(self.config, local=True)

    def test_expired_policy_is_blocked(self):
        self.config['cost_policy']['verified_on'] = (today()-timedelta(days=31)).isoformat()
        with self.assertRaises(ValueError):
            check(self.config, local=True)

    def test_valid_article_and_duplicates(self):
        validate(self.article, [], self.config)
        with self.assertRaises(ValueError):
            validate(self.article, [self.article], self.config)
        self.assertTrue(is_duplicate(self.topic, [self.article]))
        self.assertIsNone(find_topic([self.topic], [self.article], self.config))

    def test_empty_unreviewed_and_high_risk_articles_fail(self):
        for key, value in [('body',''), ('reviewed',False), ('body',self.article['body']+'治療'), ('slug','../../unsafe')]:
            article = copy.deepcopy(self.article)
            article[key] = value
            with self.assertRaises(ValueError):
                validate(article, [], self.config)

    def test_sources_reject_private_urls_and_failed_fetch(self):
        for url in ['http://developer.mozilla.org/x','https://localhost/x','https://developer.mozilla.org.evil.test/x','https://developer.mozilla.org:8443/x']:
            with self.assertRaises(ValueError):
                safe_url(url, self.config['allowed_hosts'])
        with patch('src.researcher.build_opener') as mock:
            mock.return_value.open.side_effect = OSError('offline')
            with self.assertRaises(OSError):
                research(self.topic, self.config)

    def test_history_failure_rolls_back_article(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch('src.publisher.ROOT', root), patch('src.publisher.atomic_json', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    publish(self.article, [])
            self.assertFalse((root/'posts'/ (self.article['slug']+'.md')).exists())

    def test_generated_html_and_feeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            build('https://example.github.io/write', output)
            self.assertTrue((output/'index.html').exists())
            self.assertIn('https://example.github.io/write/', (output/'sitemap.xml').read_text(encoding='utf-8'))
            for path in (output/'posts').glob('*.html'):
                text = path.read_text(encoding='utf-8')
                self.assertIn('application/ld+json', text)
                self.assertIn('rel="canonical"', text)
                self.assertIn('../assets/style.css', text)

    def test_markdown_escapes_html(self):
        result, _ = markdown('<script>alert(1)</script>')
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)

if __name__ == '__main__':
    unittest.main()

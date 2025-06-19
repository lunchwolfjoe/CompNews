import hashlib
from typing import List, Dict, Set
from database.connection import get_db
from database.models import Article

class Deduplicator:
    def __init__(self):
        pass

    def normalize(self, article: Dict) -> Dict:
        # Normalize fields: strip whitespace, standardize keys, etc.
        article["title"] = article.get("title", "").strip()
        article["content"] = article.get("content", "").strip()
        article["url"] = article.get("url", "").strip()
        if "published_date" in article and article["published_date"]:
            article["published_date"] = str(article["published_date"])
        return article

    def hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_existing_urls_and_hashes(self) -> (Set[str], Set[str]):
        urls = set()
        hashes = set()
        with get_db() as db:
            for row in db.query(Article.url, Article.content):
                urls.add(row.url)
                hashes.add(self.hash_content(row.content or ""))
        return urls, hashes

    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        urls, hashes = self.get_existing_urls_and_hashes()
        unique_articles = []
        for article in articles:
            article = self.normalize(article)
            url = article.get("url")
            content_hash = self.hash_content(article.get("content", ""))
            if url in urls or content_hash in hashes:
                continue
            unique_articles.append(article)
            urls.add(url)
            hashes.add(content_hash)
        return unique_articles 
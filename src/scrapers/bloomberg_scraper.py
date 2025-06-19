import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
import time

from scrapers.base_scraper import BaseScraper

class BloombergScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=2.0, max_retries=3)  # Bloomberg specific rate limit
        self.base_url = "https://www.bloomberg.com"
        self.search_url = f"{self.base_url}/search?query=warehouse%20wages"
        # Wrap methods with decorators
        self.scrape = self.rate_limit_decorator(self.retry_decorator(self.scrape))
        self.scrape_article = self.rate_limit_decorator(self.retry_decorator(self.scrape_article))

    def scrape(self) -> List[Dict]:
        """
        Scrape articles from Bloomberg's search results.
        """
        articles = []
        try:
            # Add proper headers to mimic browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(self.search_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            article_links = soup.select('article.story-list-story')
            
            for article in article_links:
                try:
                    link = article.select_one('a')
                    if link and 'href' in link.attrs:
                        article_url = self.base_url + link['href']
                        article_data = self.scrape_article(article_url)
                        if article_data:
                            articles.append(article_data)
                            
                except Exception as e:
                    self.handle_error(e, {"url": article_url})
                    
        except Exception as e:
            self.handle_error(e, {"url": self.search_url})
            
        return articles

    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape a single article page.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return self.parse_article(response.text, url)
            
        except Exception as e:
            self.handle_error(e, {"url": url})
            return None

    def parse_article(self, html_content: str, url: str) -> Optional[Dict]:
        """
        Parse article HTML content.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract article data
            title = soup.select_one('h1.headline')
            content = soup.select_one('div.body-copy')
            date = soup.select_one('time')
            author = soup.select_one('span.author')
            
            if not title or not content:
                return None
                
            return {
                "title": self.clean_text(title.text),
                "content": self.clean_text(content.text),
                "url": url,
                "published_date": self.extract_date(date.text) if date else None,
                "author": self.clean_text(author.text) if author else None,
                "source": "Bloomberg",
                "scraped_date": datetime.now()
            }
            
        except Exception as e:
            self.handle_error(e)
            return None 
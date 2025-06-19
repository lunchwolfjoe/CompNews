from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
import time
import logging

from scrapers.base_scraper import BaseScraper

class ReutersSeleniumScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=1.0, max_retries=3)
        self.base_url = "https://www.reuters.com"
        self.search_url = f"{self.base_url}/site-search/?query=wages"
        self.logger = logging.getLogger(self.__class__.__name__)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape(self) -> List[Dict]:
        articles = []
        try:
            self.driver.get(self.search_url)
            # Wait for search results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.search-result-content a.search-result-title'))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            article_links = soup.select('div.search-result-content a.search-result-title')
            for link in article_links[:5]:  # Limit to 5 for demo
                article_url = self.base_url + link['href']
                article_data = self.scrape_article(article_url)
                if article_data:
                    articles.append(article_data)
                time.sleep(self.rate_limit)
        except Exception as e:
            self.handle_error(e, {"url": self.search_url})
        finally:
            self.driver.quit()
        return articles

    def scrape_article(self, url: str) -> Optional[Dict]:
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1'))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            return self.parse_article(soup, url)
        except Exception as e:
            self.handle_error(e, {"url": url})
            return None

    def parse_article(self, soup: BeautifulSoup, url: str) -> Optional[Dict]:
        try:
            title = soup.select_one('h1')
            content = soup.select_one('div.article-body__content')
            if not content:
                content = soup.select_one('div.ArticleBody__content___2gQno2')
            date = soup.select_one('time')
            author = soup.select_one('span.BylineBar_byline')
            if not title or not content:
                return None
            return {
                "title": self.clean_text(title.text),
                "content": self.clean_text(content.text),
                "url": url,
                "published_date": self.extract_date(date.text) if date else None,
                "author": self.clean_text(author.text) if author else None,
                "source": "Reuters",
                "scraped_date": datetime.now()
            }
        except Exception as e:
            self.handle_error(e)
            return None 
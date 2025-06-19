import feedparser
from typing import Dict, List, Optional
from datetime import datetime
import logging
import re
import streamlit as st

from .base_scraper import BaseScraper

class GuardianScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=1.0, max_retries=3)
        # Use multiple RSS feeds for broader coverage
        self.rss_urls = [
            "https://www.theguardian.com/uk/business/rss",  # Business
            "https://www.theguardian.com/uk/money/rss",  # Money (often has compensation news)
            "https://www.theguardian.com/uk/society/rss",  # Society (often has labor news)
        ]
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Region-specific keywords for relevance detection
        self.region_keywords = {
            "North America": [
                "united states", "u.s.", "canada", "canadian", "mexico", "mexican",
                "north america", "north american", "federal reserve", "fed",
                "wall street", "nasdaq", "nyse", "treasury"
            ],
            "Europe": [
                "european union", "germany", "france", "italy", "spain", "netherlands",
                "ecb", "european central bank", "brussels", "frankfurt", "european"
            ],
            "Asia": [
                "china", "japan", "india", "singapore", "hong kong", "south korea",
                "asian markets", "bank of japan", "pboc", "nikkei"
            ],
            "UK": [
                "united kingdom", "britain", "england", "scotland", "wales",
                "bank of england", "boe", "ftse", "british"
            ],
            "Australia": [
                "australia", "new zealand", "australian", "reserve bank of australia",
                "rba", "asx"
            ]
        }

    def scrape(self) -> List[Dict]:
        """Scrape articles from The Guardian RSS feed"""
        articles = []
        
        try:
            # Fetch RSS feed
            self.logger.info("Fetching RSS feed from https://www.theguardian.com/uk/business/rss")
            feed = feedparser.parse("https://www.theguardian.com/uk/business/rss")
            
            if not feed.entries:
                self.logger.warning("No entries found in Guardian RSS feed")
                return articles
                
            self.logger.info(f"Found {len(feed.entries)} articles in RSS feed")
            
            # Process each entry
            for entry in feed.entries:
                try:
                    # Extract basic article data
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    published = self.extract_date(entry.get('published_parsed'))
                    summary = entry.get('summary', '')
                    
                    # Skip if no title or link
                    if not title or not link:
                        continue
                    
                    # Check relevance using enhanced scoring
                    is_relevant, matched_terms, relevance_score, topics = self._check_relevance(
                        title, summary, self.SEARCH_TERMS
                    )
                    
                    if is_relevant:
                        article = {
                            'title': title,
                            'url': link,
                            'content': summary,
                            'source': 'The Guardian',
                            'published_date': published,
                            'scraped_date': datetime.now(),
                            'matched_terms': matched_terms,
                            'relevance_score': relevance_score,
                            'topics': topics
                        }
                        articles.append(article)
                        self.logger.info(f"Added article: {title}")
                    else:
                        self.logger.info(f"Rejected article '{title}' (relevance score: {relevance_score:.2f})")
                        
                except Exception as e:
                    self.logger.error(f"Error processing Guardian article: {e}")
                    continue
                    
            self.logger.info(f"Successfully processed {len(articles)} relevant articles")
            return articles
            
        except Exception as e:
            self.logger.error(f"Error scraping Guardian: {e}")
            return articles

    def check_region_relevance(self, article: Dict, region: str) -> bool:
        """Check if article is relevant to the selected region"""
        if region == "Global":
            return True
            
        # Get keywords for the selected region
        keywords = self.region_keywords.get(region, [])
        if not keywords:
            return True  # If no keywords defined for region, accept all
            
        # Check title, content, and summary for region keywords
        text = f"{article['title']} {article['content']} {article.get('summary', '')}".lower()
        
        # Check for region keywords with word boundaries
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text):
                self.logger.info(f"Article matches {region} keyword: {keyword}")
                return True
                
        return False

    def parse_article(self, entry) -> Optional[Dict]:
        """Parse RSS entry into article data"""
        try:
            # Handle published date from feedparser
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                # feedparser provides published_parsed as a time struct
                import time
                published_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            elif hasattr(entry, 'published'):
                # Parse the published string and ensure it's timezone-naive
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(entry.published)
                    # Convert to timezone-naive datetime for SQLite compatibility
                    published_date = dt.replace(tzinfo=None) if dt.tzinfo else dt
                except Exception as e:
                    self.logger.warning(f"Failed to parse published date: {e}")
                    published_date = None
            
            article_data = {
                "title": self.clean_text(entry.title),
                "content": self.clean_text(entry.summary),
                "url": entry.link,
                "published_date": published_date,
                "author": self.clean_text(entry.author) if hasattr(entry, 'author') else None,
                "source": "The Guardian",
                "scraped_date": datetime.now()
            }
            
            # Add relevance data if available
            if hasattr(entry, 'matched_terms'):
                article_data['matched_terms'] = entry.matched_terms
            if hasattr(entry, 'relevance_score'):
                article_data['relevance_score'] = entry.relevance_score
            if hasattr(entry, 'topics'):
                article_data['topics'] = entry.topics
            
            return article_data
            
        except Exception as e:
            self.handle_error(e)
            return None 
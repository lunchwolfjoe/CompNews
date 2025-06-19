import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Optional
import logging
from .base_scraper import BaseScraper
import re
from urllib.parse import urljoin, urlparse
import time
import streamlit as st

logger = logging.getLogger(__name__)

class YahooFinanceScraper(BaseScraper):
    """Scraper for Yahoo Finance RSS feeds"""
    
    def __init__(self):
        super().__init__()
        self.source_name = "Yahoo Finance"
        self.base_url = "https://finance.yahoo.com"
        
        # Yahoo Finance RSS feeds - very reliable for business news
        self.rss_feeds = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC,^DJI,^IXIC&region=US&lang=en-US",  # Market headlines
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=AAPL,MSFT,GOOGL,AMZN,TSLA&region=US&lang=en-US",  # Tech stocks
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=JPM,BAC,WFC,GS,MS&region=US&lang=en-US",  # Financial stocks
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=WMT,COST,TGT&region=US&lang=en-US",  # Retail stocks (often have labor news)
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=UNH,CVS,WBA&region=US&lang=en-US",  # Healthcare stocks (often have labor news)
        ]
        
        # Default search terms for compensation-related news
        self.default_search_terms = [
            # Core compensation terms
            "compensation", "salary", "wage", "pay", "bonus", "benefits",
            "employment", "job", "hiring", "layoff", "unemployment",
            "labor", "union", "strike", "minimum wage", "equal pay",
            "income", "earnings", "revenue", "profit", "economy",
            "inflation", "cost of living", "pension", "retirement",
            "workplace", "employee", "employer", "payroll", "tax",
            
            # Government and public sector
            "police", "firefighter", "teacher", "government employee", "public employee",
            "civil servant", "municipal", "state employee", "federal employee",
            "law enforcement", "police department", "fire department",
            "teacher union", "police union", "fire union",
            
            # Specific compensation terms
            "pay raise", "salary increase", "wage hike", "bonus package",
            "compensation package", "benefit package", "overtime pay",
            "hazard pay", "shift differential", "holiday pay",
            "performance bonus", "signing bonus", "retention bonus",
            "executive pay", "CEO pay", "board compensation",
            
            # Labor and employment
            "collective bargaining", "union contract", "labor dispute",
            "workforce", "staffing", "recruitment", "talent",
            "job market", "labor shortage", "employment rate",
            "job cuts", "downsizing", "restructuring", "severance",
            
            # Industry specific
            "healthcare worker", "nurse", "doctor", "hospital employee",
            "tech worker", "software engineer", "developer",
            "manufacturing worker", "factory worker", "warehouse worker",
            "retail worker", "service worker", "gig worker",
            
            # Financial terms (Yahoo Finance specific)
            "stock", "market", "trading", "investment", "finance",
            "earnings", "quarterly results", "financial results"
        ]
        
        # Region keywords for filtering
        self.region_keywords = {
            "North America": ["united states", "u.s.", "canada", "canadian", "mexico", "mexican", "north america", "north american"],
            "Europe": ["european union", "germany", "france", "italy", "spain", "netherlands", "european"],
            "Asia": ["china", "japan", "india", "singapore", "hong kong", "south korea", "asian markets"],
            "UK": ["united kingdom", "britain", "england", "scotland", "wales", "british"],
            "Australia": ["australia", "new zealand", "australian"]
        }

    def scrape(self) -> List[Dict]:
        """Scrape articles from Yahoo Finance RSS feeds"""
        articles = []
        
        try:
            # Fetch RSS feeds
            self.logger.info(f"Fetching RSS feeds from {', '.join(self.rss_feeds)}")
            for rss_url in self.rss_feeds:
                try:
                    feed = feedparser.parse(rss_url)
                    
                    if feed.bozo:
                        self.logger.error(f"RSS Feed Error for {rss_url}: {feed.bozo_exception}")
                        continue
                    
                    if not feed.entries:
                        self.logger.warning(f"No entries found in {rss_url}")
                        continue
                        
                    self.logger.info(f"Found {len(feed.entries)} articles in {rss_url} RSS feed")
                    
                    # Process each entry
                    for entry in feed.entries:
                        try:
                            # Check if article matches search terms
                            if self.is_relevant(entry):
                                article_data = self.parse_article(entry)
                                if article_data:
                                    articles.append(article_data)
                                    self.logger.info(f"Yahoo Finance: Added article: {article_data['title']}")
                            else:
                                self.logger.debug(f"Skipped irrelevant article: {entry.title}")
                        except Exception as e:
                            self.logger.error(f"Error processing entry {entry.get('title', 'Unknown')}: {str(e)}")
                            continue
                    
                    self.logger.info(f"Successfully processed {len([a for a in articles if a.get('source') == 'Yahoo Finance'])} relevant articles from {rss_url}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing RSS feed {rss_url}: {str(e)}")
                    continue
                    
            self.logger.info(f"Successfully processed {len(articles)} relevant articles from all feeds")
            
            if not articles:
                st.warning("No relevant articles found. Try adjusting the search terms.")
            
            return articles[:10]  # Limit to 10 most recent articles
            
        except Exception as e:
            self.handle_error(e, {"urls": self.rss_feeds})
            st.error(f"Error scraping articles: {str(e)}")
            return []

    def _process_entry(self, entry) -> Optional[Dict]:
        """Process a single RSS entry"""
        try:
            # Extract basic information
            title = entry.get('title', '').strip()
            if not title:
                return None
                
            # Get link
            link = entry.get('link', '')
            if not link:
                return None
            
            # Get published date
            published_date = self._parse_date(entry.get('published', ''))
            if not published_date:
                published_date = datetime.now()
            
            # Get content/summary
            content = entry.get('summary', '')
            if not content:
                content = entry.get('description', '')
            
            # Clean content
            content = self._clean_content(content)
            
            # Get author/source
            author = entry.get('author', '')
            if not author:
                author = "Yahoo Finance"
            
            # Check relevance using new method
            search_terms = st.session_state.get('search_terms', self.default_search_terms)
            
            is_relevant, matched_terms, relevance_score, topics = self._check_relevance(title, content, search_terms)
            
            if not is_relevant and search_terms:
                logger.debug(f"Yahoo Finance article not relevant: {title}")
                return None
            
            article = {
                'title': title,
                'content': content,
                'url': link,
                'published_date': published_date,
                'author': author,
                'source': self.source_name,
                'scraped_date': datetime.now(),
                'matched_terms': matched_terms,
                'relevance_score': relevance_score,
                'topics': topics
            }
            
            logger.info(f"Yahoo Finance: Added article: {title}")
            return article
            
        except Exception as e:
            logger.error(f"Error processing Yahoo Finance entry: {e}")
            return None

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string from RSS feed"""
        if not date_str:
            return None
            
        try:
            # Try different date formats
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S %Z',
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S'
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, try parsing with dateutil
            from dateutil import parser
            return parser.parse(date_str)
            
        except Exception as e:
            logger.warning(f"Could not parse date '{date_str}': {e}")
            return None

    def _clean_content(self, content: str) -> str:
        """Clean and format content"""
        if not content:
            return ""
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove special characters that might cause issues
        content = content.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        
        return content.strip()

    def _check_relevance(self, title: str, content: str, search_terms: List[str]) -> tuple[bool, List[str], float, List[str]]:
        """Use the base scraper's enhanced relevance checking method"""
        return super()._check_relevance(title, content, search_terms)

    def parse_article(self, html_content: str) -> Optional[Dict]:
        """Parse a single article's HTML content"""
        # This method is not used for RSS scraping
        return None 
import feedparser
from typing import Dict, List, Optional
from datetime import datetime
import logging
import streamlit as st

from scrapers.base_scraper import BaseScraper

class ReutersRSSScraper(BaseScraper):
    def __init__(self):
        super().__init__(rate_limit=1.0, max_retries=3)
        # Try a different Reuters RSS feed that's more accessible
        self.rss_url = "https://www.reuters.com/arc/outboundfeeds/rss/"
        self.logger = logging.getLogger(self.__class__.__name__)

    def scrape(self) -> List[Dict]:
        articles = []
        try:
            self.logger.info(f"Fetching RSS feed from {self.rss_url}")
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                self.logger.error(f"RSS Feed Error: {feed.bozo_exception}")
                st.error(f"Error reading Reuters RSS feed: {feed.bozo_exception}")
                return []
            
            if not feed.entries:
                self.logger.warning("No entries found in Reuters RSS feed")
                st.warning("No articles found in the Reuters RSS feed")
                return []
            
            self.logger.info(f"Found {len(feed.entries)} articles in Reuters RSS feed")
            
            # Get current region filter
            current_region = st.session_state.get('region_filter', 'Global')
            self.logger.info(f"Current region filter: {current_region}")
            
            # Process each entry
            for entry in feed.entries[:10]:  # Limit to 10 for demo
                try:
                    # Check if article matches search terms
                    if self.is_relevant(entry):
                        article_data = self.parse_article(entry)
                        if article_data:
                            # Check region relevance
                            is_region_relevant = self.check_region_relevance(article_data, current_region)
                            if current_region == "Global" or is_region_relevant:
                                articles.append(article_data)
                                self.logger.info(f"Added Reuters article: {article_data['title']}")
                            else:
                                self.logger.debug(f"Skipped Reuters article due to region filter: {entry.title}")
                    else:
                        self.logger.debug(f"Skipped irrelevant Reuters article: {entry.title}")
                except Exception as e:
                    self.logger.error(f"Error processing Reuters entry {entry.get('title', 'Unknown')}: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully processed {len(articles)} relevant Reuters articles")
            
            if not articles:
                if current_region != "Global":
                    st.warning(f"No Reuters articles found matching the {current_region} region filter.")
                else:
                    st.warning("No relevant Reuters articles found. Try adjusting the search terms.")
            
            return articles
            
        except Exception as e:
            self.handle_error(e, {"url": self.rss_url})
            st.error(f"Error scraping Reuters articles: {str(e)}")
            return []

    def is_relevant(self, entry) -> bool:
        """Check if article matches search terms"""
        # Get search terms from session state, fallback to defaults if not set
        search_terms = st.session_state.get('search_terms', [
            "compensation", "salary", "wage", "pay gap", "minimum wage",
            "equal pay", "benefits", "remuneration", "bonus", "payroll",
            "labor market", "employment cost", "income inequality"
        ])
        
        # Check title and summary for search terms
        text = f"{entry.title} {entry.summary}".lower()
        matches = []
        
        for term in search_terms:
            if term.lower() in text:
                matches.append(term)
        
        if matches:
            self.logger.info(f"Reuters article '{entry.title}' matched terms: {', '.join(set(matches))}")
            return True
            
        # If no search terms are set or no matches, accept all articles for now
        if not search_terms or search_terms == ["compensation", "salary", "wage", "pay gap", "minimum wage", "equal pay", "benefits", "remuneration", "bonus", "payroll", "labor market", "employment cost", "income inequality"]:
            self.logger.info(f"Accepting Reuters article '{entry.title}' (no specific search terms or default terms)")
            return True
            
        return False

    def check_region_relevance(self, article: Dict, region: str) -> bool:
        """Check if article is relevant to the selected region using base scraper's method"""
        if region == "Global":
            return True
            
        # Use base scraper's region matching with word boundaries
        is_region_match = self._check_region_match(article['title'], article['content'], region)
        if is_region_match:
            self.logger.info(f"Reuters article matches {region} region")
            return True
            
        return False

    def parse_article(self, entry) -> Optional[Dict]:
        try:
            # Handle published date
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                import time
                published_date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            elif hasattr(entry, 'published'):
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(entry.published)
                    published_date = dt.replace(tzinfo=None) if dt.tzinfo else dt
                except Exception as e:
                    self.logger.warning(f"Failed to parse Reuters published date: {e}")
                    published_date = None
            
            article_data = {
                "title": self.clean_text(entry.title),
                "content": self.clean_text(entry.summary),
                "url": entry.link,
                "published_date": published_date,
                "author": self.clean_text(entry.author) if hasattr(entry, 'author') else None,
                "source": "Reuters",
                "scraped_date": datetime.now()
            }
            
            # Log the matched search terms for this article
            if hasattr(entry, 'summary'):
                search_terms = st.session_state.get('search_terms', [])
                matches = [term for term in search_terms if term.lower() in entry.summary.lower()]
                if matches:
                    article_data['matched_terms'] = matches
                    self.logger.info(f"Reuters article matched terms: {', '.join(matches)}")
            
            return article_data
            
        except Exception as e:
            self.handle_error(e)
            return None 
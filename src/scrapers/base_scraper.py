from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging
from datetime import datetime
import time
from functools import wraps
import re

class BaseScraper(ABC):
    def __init__(self, rate_limit: float = 1.0, max_retries: int = 3):
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.last_request = 0
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Enhanced search terms for compensation and labor-related content
        self.SEARCH_TERMS = [
            "compensation", "salary", "wage", "pay gap", "minimum wage",
            "equal pay", "benefits", "remuneration", "bonus", "payroll",
            "labor market", "employment cost", "income inequality",
            "pay raise", "salary increase", "wage hike", "pay cut",
            "overtime pay", "severance pay", "stock options", "equity compensation",
            "executive pay", "CEO compensation", "board compensation",
            "union wages", "collective bargaining", "strike", "labor dispute",
            "cost of living", "inflation adjustment", "merit pay", "performance bonus",
            "commission", "tips", "gratuity", "hazard pay", "shift differential",
            "holiday pay", "sick pay", "vacation pay", "parental leave",
            "health insurance", "retirement benefits", "401k", "pension",
            "workers compensation", "unemployment benefits", "social security",
            "tax credits", "earned income", "living wage", "fair pay",
            "gender pay gap", "racial pay gap", "age discrimination",
            "overtime", "part-time", "full-time", "contractor", "freelancer",
            "gig economy", "platform workers", "remote work", "hybrid work",
            "work from home", "flexible scheduling", "work-life balance"
        ]
        
        # Negative keywords to filter out irrelevant content
        self.NEGATIVE_KEYWORDS = [
            "sports salary", "athlete salary", "celebrity salary", "actor salary",
            "movie salary", "film salary", "entertainment salary", "music salary",
            "singer salary", "rapper salary", "football salary", "basketball salary",
            "baseball salary", "soccer salary", "hockey salary", "golf salary",
            "tennis salary", "boxing salary", "ufc salary", "wrestling salary",
            "reality tv salary", "tv show salary", "game show salary",
            "lottery winner", "inheritance", "trust fund", "family money",
            "crypto trading", "bitcoin mining", "nft sales", "cryptocurrency",
            "gambling winnings", "casino earnings", "poker winnings"
        ]
        
        # Topic-based keyword matching for better relevance scoring
        self.TOPIC_KEYWORDS = {
            "compensation": {
                "salary": ["annual salary", "base salary", "starting salary", "salary range", "salary survey", "salary data"],
                "wage": ["hourly wage", "minimum wage", "living wage", "wage increase", "wage freeze", "wage cut"],
                "pay": ["equal pay", "pay gap", "pay raise", "pay cut", "pay equity", "pay transparency"],
                "bonus": ["performance bonus", "signing bonus", "retention bonus", "annual bonus", "quarterly bonus"],
                "benefits": ["health benefits", "retirement benefits", "employee benefits", "benefits package"],
                "equity": ["stock options", "equity compensation", "RSUs", "restricted stock", "stock grants"]
            },
            "labor_market": {
                "employment": ["job market", "employment rate", "unemployment", "job creation", "job loss"],
                "hiring": ["hiring freeze", "layoffs", "job cuts", "recruitment", "talent acquisition"],
                "union": ["labor union", "collective bargaining", "union contract", "union negotiations"],
                "strike": ["labor strike", "work stoppage", "picketing", "strike authorization"],
                "workplace": ["workplace safety", "workplace rights", "workplace discrimination"]
            },
            "government": {
                "policy": ["labor policy", "employment law", "minimum wage law", "overtime law"],
                "regulation": ["wage regulation", "benefits regulation", "workplace regulation"],
                "legislation": ["pay equity bill", "minimum wage bill", "overtime bill"],
                "enforcement": ["wage theft", "labor violations", "compliance", "investigation"]
            },
            "industry": {
                "tech": ["tech salaries", "startup compensation", "tech benefits", "tech equity"],
                "finance": ["banking compensation", "finance bonuses", "wall street pay"],
                "healthcare": ["nurse pay", "doctor salaries", "healthcare benefits"],
                "education": ["teacher salaries", "education funding", "school budgets"],
                "retail": ["retail wages", "retail benefits", "retail unionization"],
                "manufacturing": ["factory wages", "manufacturing pay", "industrial compensation"]
            }
        }

    def rate_limit_decorator(self, func):
        """
        Decorator to enforce rate limiting on methods.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            time_since_last_request = current_time - self.last_request
            
            if time_since_last_request < self.rate_limit:
                sleep_time = self.rate_limit - time_since_last_request
                self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            self.last_request = time.time()
            return func(*args, **kwargs)
        return wrapper

    def retry_decorator(self, func):
        """
        Decorator to handle retries for failed requests.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        self.handle_error(e, {"attempt": attempt + 1})
                        raise
                    self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(2 ** attempt)  # Exponential backoff
            return None
        return wrapper

    @abstractmethod
    def scrape(self) -> List[Dict]:
        """
        Main method to scrape articles from the source.
        Returns a list of article dictionaries.
        """
        pass

    @abstractmethod
    def parse_article(self, html_content: str) -> Optional[Dict]:
        """
        Parse a single article's HTML content.
        Returns a dictionary with article data or None if parsing fails.
        """
        pass

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        """
        if not text:
            return ""
        return " ".join(text.split())

    def extract_date(self, date_input) -> Optional[datetime]:
        """
        Extract and parse date from various formats.
        """
        try:
            if date_input is None:
                return None
                
            # If it's already a datetime object, return it
            if isinstance(date_input, datetime):
                return date_input
                
            # If it's a string, try to parse it with basic formats
            if isinstance(date_input, str):
                # Try ISO format first
                try:
                    return datetime.fromisoformat(date_input.replace('Z', '+00:00'))
                except:
                    pass
                # Try common RSS format: "Thu, 19 Jun 2025 09:00:00 GMT"
                try:
                    from email.utils import parsedate_to_datetime
                    return parsedate_to_datetime(date_input)
                except:
                    pass
                
            # If it's a time struct (from feedparser), convert it
            if hasattr(date_input, 'tm_year'):
                import time
                return datetime.fromtimestamp(time.mktime(date_input))
                
            return None
        except Exception as e:
            self.logger.error(f"Error parsing date: {e}")
            return None

    def handle_error(self, error: Exception, context: Dict = None):
        """
        Handle errors during scraping.
        """
        self.logger.error(f"Error during scraping: {error}", extra=context or {})
        # Add error handling logic here 

    def _check_relevance(self, title: str, content: str, search_terms: List[str]) -> tuple[bool, List[str], float, List[str]]:
        """
        Enhanced relevance checking with contextual matching and topic classification.
        Returns: (is_relevant, matched_terms, relevance_score, topics)
        """
        if not search_terms:
            return True, [], 0.0, []
            
        text = f"{title.lower()} {content.lower()}"
        matched_terms = []
        matched_topics = set()
        relevance_score = 0.0
        
        # Check for negative keywords first
        for neg_term in self.NEGATIVE_KEYWORDS:
            if re.search(r'\b' + re.escape(neg_term.lower()) + r'\b', text):
                return False, [], 0.0, []
        
        # Check for exact phrase matches first
        for topic, keyword_dict in self.TOPIC_KEYWORDS.items():
            for keyword, phrases in keyword_dict.items():
                # Look for contextual phrases first (higher priority)
                for phrase in phrases:
                    if re.search(r'\b' + re.escape(phrase.lower()) + r'\b', text):
                        matched_terms.append(phrase)
                        matched_topics.add(topic)
                        # Higher score for contextual matches
                        relevance_score += 0.4
                        
                # Also check for the main keyword with word boundaries
                if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text):
                    if keyword not in matched_terms:  # Avoid double counting
                        matched_terms.append(keyword)
                        matched_topics.add(topic)
                        # Base score for single keyword matches
                        relevance_score += 0.2
        
        # Title matches get extra weight
        title_lower = title.lower()
        for term in matched_terms:
            if re.search(r'\b' + re.escape(term.lower()) + r'\b', title_lower):
                relevance_score += 0.3
        
        # Normalize score
        relevance_score = min(relevance_score, 1.0)
        
        # Lower threshold to catch more relevant articles
        if relevance_score < 0.1:  # Lowered from 0.2 to 0.1
            return False, [], 0.0, []
        
        return bool(matched_terms), matched_terms, relevance_score, list(matched_topics) 
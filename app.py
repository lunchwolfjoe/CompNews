import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="CompNews - Compensation News Aggregator",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import get_db, init_db
from database.models import Article, Source
from scrapers.guardian_scraper import GuardianScraper
from scrapers.ap_scraper import APScraper
from scrapers.google_news_scraper import GoogleNewsScraper
from scrapers.yahoo_finance_scraper import YahooFinanceScraper
from sqlalchemy.orm import Session
from typing import List, Dict
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'search_terms' not in st.session_state:
        st.session_state.search_terms = [
            "compensation", "salary", "wage", "pay gap", "minimum wage",
            "equal pay", "benefits", "remuneration", "bonus", "payroll",
            "labor market", "employment cost", "income inequality"
        ]
    if 'sources' not in st.session_state:
        st.session_state.sources = ["The Guardian", "Associated Press", "Google News", "Yahoo Finance"]
    if 'db_session' not in st.session_state:
        st.session_state.db_session = None

def get_db_session():
    """Get or create database session"""
    if st.session_state.db_session is None:
        st.session_state.db_session = get_db().__enter__()
    return st.session_state.db_session

def scrape_articles() -> List[Dict]:
    """Scrape articles from all enabled sources"""
    articles = []
    seen_urls = set()
    db = get_db_session()
    
    try:
        if "The Guardian" in st.session_state.sources:
            guardian_scraper = GuardianScraper()
            articles.extend(guardian_scraper.scrape())
            
        if "Associated Press" in st.session_state.sources:
            ap_scraper = APScraper()
            articles.extend(ap_scraper.scrape())
            
        if "Google News" in st.session_state.sources:
            google_scraper = GoogleNewsScraper()
            articles.extend(google_scraper.scrape())
            
        if "Yahoo Finance" in st.session_state.sources:
            yahoo_scraper = YahooFinanceScraper()
            articles.extend(yahoo_scraper.scrape())
            
        # Save new articles to database
        for article_data in articles:
            url = article_data['url']
            if url in seen_urls:
                continue
            seen_urls.add(url)
            # Check if article already exists in DB
            existing = db.query(Article).filter(Article.url == url).first()
            if not existing:
                # Convert matched_terms to JSON string if it's a list
                if 'matched_terms' in article_data and isinstance(article_data['matched_terms'], list):
                    article_data['matched_terms'] = json.dumps(article_data['matched_terms'])
                
                # Convert topics to JSON string if it's a list
                if 'topics' in article_data and isinstance(article_data['topics'], list):
                    article_data['topics'] = json.dumps(article_data['topics'])
                
                # Remove any fields that don't exist in the model
                model_fields = ['id', 'title', 'content', 'url', 'source', 'published_date', 
                               'scraped_date', 'author', 'category', 'article_metadata', 
                               'entities', 'matched_terms', 'relevance_score', 
                               'topics', 'created_at', 'updated_at']
                filtered_data = {k: v for k, v in article_data.items() if k in model_fields}
                
                # Remove region_match if it exists
                if 'region_match' in filtered_data:
                    del filtered_data['region_match']
                
                article = Article(**filtered_data)
                db.add(article)
        db.commit()
        logger.info(f"Saved {len(seen_urls)} new articles to database")
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        st.error(f"Error during scraping: {str(e)}")
        db.rollback()
    return articles

def get_articles_from_db(days: int = 7) -> List[Dict]:
    """Get articles from database with filtering"""
    db = get_db_session()
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = db.query(Article).filter(Article.published_date >= cutoff_date)
        logger.info(f"DB filter: published_date >= {cutoff_date}")
        
        # Apply source filter
        if st.session_state.sources:
            query = query.filter(Article.source.in_(st.session_state.sources))
            logger.info(f"DB filter: sources in {st.session_state.sources}")
            
        # Apply relevance score filter
        min_relevance = 0.1  # Lowered from 0.2 to catch more relevant articles
        query = query.filter(Article.relevance_score >= min_relevance)
        logger.info(f"DB filter: relevance_score >= {min_relevance}")
        
        # Order by relevance score and date
        query = query.order_by(Article.relevance_score.desc(), Article.published_date.desc())
        
        # Execute query and get all results while session is still active
        articles = query.all()
        logger.info(f"DB returned {len(articles)} articles after filtering")
        
        # Convert to dicts for display
        article_dicts = []
        for article in articles:
            # Access all SQLAlchemy model attributes while session is active
            matched_terms = []
            if article.matched_terms:
                try:
                    matched_terms = json.loads(article.matched_terms)
                except:
                    matched_terms = []
                    
            topics = []
            if article.topics:
                try:
                    topics = json.loads(article.topics)
                except:
                    topics = []
                    
            article_dict = {
                'title': str(article.title),
                'content': str(article.content) if article.content else '',
                'url': str(article.url),
                'source': str(article.source),
                'published_date': article.published_date.strftime('%Y-%m-%d %H:%M:%S') if article.published_date else '',
                'relevance_score': float(article.relevance_score) if article.relevance_score else 0.0,
                'matched_terms': matched_terms,
                'topics': topics
            }
            
            # Add relevance indicator
            if article_dict['relevance_score'] >= 0.7:
                article_dict['relevance_indicator'] = '🟢'  # High relevance
            elif article_dict['relevance_score'] >= 0.4:
                article_dict['relevance_indicator'] = '🟡'  # Medium relevance
            else:
                article_dict['relevance_indicator'] = '🔴'  # Low relevance
                
            article_dicts.append(article_dict)
        
        logger.info(f"Returning {len(article_dicts)} article dicts to UI")
        return article_dicts
        
    except Exception as e:
        logger.error(f"Error fetching articles from database: {e}")
        st.error(f"Error fetching articles: {str(e)}")
        return []

def group_similar_articles(articles: List[Dict]) -> List[Dict]:
    """Group similar articles together based on title and content similarity"""
    from difflib import SequenceMatcher
    
    def similarity_score(str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def are_articles_similar(article1: Dict, article2: Dict) -> bool:
        """Determine if two articles are similar enough to be grouped"""
        title_similarity = similarity_score(article1['title'], article2['title'])
        # If titles are very similar, consider them the same story
        if title_similarity > 0.7:
            return True
            
        # If they share multiple matched terms and have similar topics, consider them related
        terms1 = set(article1.get('matched_terms', []))
        terms2 = set(article2.get('matched_terms', []))
        topics1 = set(article1.get('topics', []))
        topics2 = set(article2.get('topics', []))
        
        terms_overlap = len(terms1.intersection(terms2)) / max(len(terms1.union(terms2)), 1)
        topics_overlap = len(topics1.intersection(topics2)) / max(len(topics1.union(topics2)), 1)
        
        return terms_overlap > 0.5 and topics_overlap > 0.3

    # Initialize groups
    article_groups = []
    used_articles = set()
    
    # Sort articles by relevance score and date
    sorted_articles = sorted(
        articles, 
        key=lambda x: (float(x.get('relevance_score', 0)), x.get('published_date', '')), 
        reverse=True
    )
    
    # Group articles
    for i, article in enumerate(sorted_articles):
        if i in used_articles:
            continue
            
        current_group = [article]
        used_articles.add(i)
        
        # Look for similar articles
        for j, other_article in enumerate(sorted_articles):
            if j in used_articles:
                continue
                
            if are_articles_similar(article, other_article):
                current_group.append(other_article)
                used_articles.add(j)
        
        # Add group to results
        if len(current_group) > 1:
            # Sort group by relevance score
            current_group = sorted(current_group, key=lambda x: float(x.get('relevance_score', 0)), reverse=True)
            article_groups.append({
                'main_article': current_group[0],
                'related_articles': current_group[1:]
            })
        else:
            article_groups.append({
                'main_article': current_group[0],
                'related_articles': []
            })
    
    return article_groups

def display_article_group(group: Dict):
    """Display a group of related articles"""
    main_article = group['main_article']
    related_articles = group['related_articles']

    # Short summary (first 30 words or 200 chars)
    def short_summary(text, word_limit=30, char_limit=200):
        if not text:
            return ''
        words = text.split()
        if len(words) > word_limit:
            return ' '.join(words[:word_limit]) + '...'
        if len(text) > char_limit:
            return text[:char_limit] + '...'
        return text

    main_title = f"{main_article.get('relevance_indicator', '')} {main_article['title']}"
    main_short = short_summary(main_article.get('content', ''), 30, 200)
    related_count = len(related_articles)
    expander_label = f"{main_title}\n\n{main_short}\n\n{related_count} related article{'s' if related_count != 1 else ''}. Click to expand."

    with st.expander(expander_label, expanded=False):
        # Main article details
        st.markdown(f"## {main_article['title']}")
        st.write(f"**Source:** {main_article['source']}")
        st.write(f"**Published:** {main_article['published_date']}")
        if main_article.get('matched_terms'):
            st.write("**Matched Terms:**", ", ".join(str(term) for term in main_article['matched_terms']))
        if main_article.get('topics'):
            st.write("**Topics:**", ", ".join(str(topic) for topic in main_article['topics']))
        st.write("---")
        st.write(main_article.get('content', 'No content available'))
        st.write("---")
        st.write(f"[Read full article]({main_article['url']})")

        # Related articles section
        if related_articles:
            st.write(f"### {related_count} Related Article{'s' if related_count != 1 else ''}")
            
            # Create columns for related articles
            cols = st.columns(min(3, len(related_articles)))  # Up to 3 columns
            for idx, article in enumerate(related_articles):
                col = cols[idx % len(cols)]
                with col:
                    st.markdown(f"**{article['title']}**")
                    st.write(f"_{article['source']} - {article['published_date']}_")
                    st.write(short_summary(article.get('content', '')))
                    st.write(f"[Read article]({article['url']})")
                    st.write("---")

def main():
    st.title("📰 CompNews - Compensation News Aggregator")
    st.markdown("Stay informed about compensation trends, wage policies, and labor market developments")
    
    # Initialize database
    try:
        init_db()
    except Exception as e:
        st.error(f"Database initialization error: {e}")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Settings")
        
        # Search terms configuration
        st.subheader("🔍 Search Terms")
        search_terms = st.text_area(
            "Enter search terms (one per line)",
            value="\n".join(st.session_state.search_terms),
            help="These terms are used to identify relevant articles during scraping. Leave empty to accept all articles."
        )
        st.session_state.search_terms = [term.strip() for term in search_terms.split("\n") if term.strip()]
        
        # Date range filter
        st.subheader("📅 Date Range")
        days_back = st.slider(
            "Show articles from last N days",
            min_value=1,
            max_value=30,
            value=7,
            help="Filter articles by how recent they are"
        )
        
        # Source selection
        st.subheader("📰 News Sources")
        all_sources = ["The Guardian", "Associated Press", "Google News", "Yahoo Finance"]
        selected_sources = st.multiselect(
            "Select news sources",
            options=all_sources,
            default=st.session_state.sources,
            help="Choose which news sources to include"
        )
        st.session_state.sources = selected_sources
        
        # Scrape button
        if st.button("🔄 Scrape New Articles"):
            with st.spinner("Scraping articles..."):
                scrape_articles()
            st.success("Scraping completed!")
    
    # Main content area
    articles = get_articles_from_db(days=days_back)
    
    # Display articles
    if not articles:
        st.warning("No articles found. Try adjusting your filters or scraping new articles.")
    else:
        # Group similar articles
        article_groups = group_similar_articles(articles)
        st.info(f"Found {len(articles)} articles in {len(article_groups)} groups")
        
        # Display article groups
        for group in article_groups:
            display_article_group(group)

if __name__ == "__main__":
    main() 
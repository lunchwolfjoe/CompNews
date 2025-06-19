#!/usr/bin/env python3
"""
Test script for the new scrapers
"""

import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.ap_scraper import APScraper
from scrapers.google_news_scraper import GoogleNewsScraper
from scrapers.yahoo_finance_scraper import YahooFinanceScraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scrapers():
    """Test all new scrapers"""
    
    # Mock session state for testing
    import streamlit as st
    if not hasattr(st, 'session_state'):
        st.session_state = {}
    
    st.session_state['search_terms'] = [
        "compensation", "salary", "wage", "pay", "bonus", "benefits",
        "employment", "job", "hiring", "layoff", "unemployment"
    ]
    st.session_state['region_filter'] = "Global"
    
    scrapers = [
        ("Associated Press", APScraper()),
        ("Google News", GoogleNewsScraper()),
        ("Yahoo Finance", YahooFinanceScraper())
    ]
    
    for name, scraper in scrapers:
        print(f"\n{'='*50}")
        print(f"Testing {name} Scraper")
        print(f"{'='*50}")
        
        try:
            articles = scraper.scrape()
            print(f"✅ {name}: Found {len(articles)} articles")
            
            if articles:
                print(f"Sample articles from {name}:")
                for i, article in enumerate(articles[:3]):  # Show first 3
                    print(f"  {i+1}. {article['title']}")
                    print(f"     Source: {article['source']}")
                    print(f"     URL: {article['url']}")
                    print(f"     Matched terms: {article['matched_terms']}")
                    print()
            
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_scrapers() 
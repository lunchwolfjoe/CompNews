#!/usr/bin/env python3
"""
Test script to verify the improved search and filtering logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.scrapers.base_scraper import BaseScraper
from src.scrapers.google_news_scraper import GoogleNewsScraper
from src.scrapers.guardian_scraper import GuardianScraper
from src.scrapers.yahoo_finance_scraper import YahooFinanceScraper
from src.scrapers.ap_scraper import APScraper

def test_relevance_scoring():
    """Test the improved relevance scoring"""
    print("Testing improved relevance scoring...")
    
    # Create a test scraper
    scraper = BaseScraper()
    
    # Test cases with expected results
    test_cases = [
        {
            "title": "Houston Police Department Announces 15% Pay Raise for Officers",
            "content": "The Houston Police Department has approved a significant pay increase for all officers, including base salary adjustments and improved benefits package.",
            "expected_score": 0.9,  # Should be high due to police + pay raise
            "expected_terms": ["police", "pay raise", "salary"]
        },
        {
            "title": "Microsoft Plans Thousands of Job Cuts. How AI Is Reshaping the Labor Market.",
            "content": "Microsoft announced layoffs affecting thousands of employees as the company restructures its workforce.",
            "expected_score": 0.6,  # Should be medium due to job cuts + labor market
            "expected_terms": ["job cuts", "layoffs", "labor market"]
        },
        {
            "title": "Amazon Is Giving Six PC Games Away for Free Right Now",
            "content": "Amazon is offering free PC games as part of their summer promotion.",
            "expected_score": 0.0,  # Should be low/irrelevant
            "expected_terms": []
        },
        {
            "title": "Teachers Union Negotiates New Contract with 8% Salary Increase",
            "content": "The local teachers union has successfully negotiated a new contract that includes an 8% salary increase and improved benefits.",
            "expected_score": 0.8,  # Should be high due to teacher + union + salary increase
            "expected_terms": ["teacher", "union", "salary increase"]
        }
    ]
    
    search_terms = [
        "compensation", "salary", "wage", "pay", "bonus", "benefits",
        "employment", "job", "hiring", "layoff", "unemployment",
        "labor", "union", "strike", "minimum wage", "equal pay",
        "police", "firefighter", "teacher", "government employee",
        "pay raise", "salary increase", "wage hike", "bonus package"
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest case {i+1}: {test_case['title']}")
        
        is_relevant, matched_terms, relevance_score, topics = scraper._check_relevance(
            test_case['title'], 
            test_case['content'], 
            search_terms
        )
        
        print(f"  Expected score: {test_case['expected_score']}")
        print(f"  Actual score: {relevance_score}")
        print(f"  Is relevant: {is_relevant}")
        print(f"  Matched terms: {matched_terms}")
        print(f"  Topics: {topics}")
        
        # Check if score is reasonable
        if relevance_score >= 0.1:  # Our new threshold
            print(f"  ✅ PASS: Article would be included (score >= 0.1)")
        else:
            print(f"  ❌ FAIL: Article would be excluded (score < 0.1)")
        
        # Check if expected terms are found
        found_expected = any(term in matched_terms for term in test_case['expected_terms'])
        if found_expected:
            print(f"  ✅ PASS: Expected terms found")
        else:
            print(f"  ⚠️  WARNING: Expected terms not found")

def test_scrapers():
    """Test the scrapers with improved search terms"""
    print("\n" + "="*50)
    print("Testing scrapers with improved search terms...")
    
    scrapers = [
        GoogleNewsScraper(),
        GuardianScraper(),
        YahooFinanceScraper(),
        APScraper()
    ]
    
    for scraper in scrapers:
        print(f"\nTesting {scraper.__class__.__name__}...")
        print(f"Default search terms count: {len(scraper.default_search_terms)}")
        print(f"Sample terms: {scraper.default_search_terms[:5]}...")
        
        # Check if it has police-related terms
        police_terms = [term for term in scraper.default_search_terms if 'police' in term.lower()]
        if police_terms:
            print(f"  ✅ Has police terms: {police_terms}")
        else:
            print(f"  ❌ Missing police terms")

if __name__ == "__main__":
    test_relevance_scoring()
    test_scrapers()
    print("\n" + "="*50)
    print("Test completed!") 
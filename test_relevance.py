#!/usr/bin/env python3
"""
Test script for the new relevance checking functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapers.guardian_scraper import GuardianScraper

def test_relevance_checking():
    """Test the new contextual relevance checking"""
    
    # Create a scraper instance
    scraper = GuardianScraper()
    
    # Test cases
    test_cases = [
        {
            "title": "Performance bonus increased for top executives",
            "content": "The company announced a 20% increase in performance bonuses for senior management.",
            "search_terms": ["bonus", "salary", "compensation"],
            "expected_relevant": True,
            "description": "Should match 'performance bonus' contextually"
        },
        {
            "title": "Shopping bonus offers available this weekend",
            "content": "Get 10% bonus on all purchases when you use our credit card.",
            "search_terms": ["bonus", "salary", "compensation"],
            "expected_relevant": False,
            "description": "Should NOT match shopping bonus contextually"
        },
        {
            "title": "Employee salary review process begins",
            "content": "Annual salary reviews will be conducted next month for all staff.",
            "search_terms": ["salary", "wage", "compensation"],
            "expected_relevant": True,
            "description": "Should match 'salary review' contextually"
        },
        {
            "title": "Minimum wage increase approved by Congress",
            "content": "The federal minimum wage will increase to $15 per hour.",
            "search_terms": ["wage", "minimum wage", "compensation"],
            "expected_relevant": True,
            "description": "Should match 'minimum wage' contextually"
        }
    ]
    
    print("Testing new relevance checking functionality...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Title: {test_case['title']}")
        print(f"Content: {test_case['content']}")
        print(f"Search terms: {test_case['search_terms']}")
        
        # Test the relevance checking
        is_relevant, matched_terms, relevance_score, topics = scraper._check_relevance(
            test_case['title'],
            test_case['content'],
            test_case['search_terms']
        )
        
        print(f"Result: Relevant={is_relevant}, Score={relevance_score:.2f}")
        print(f"Matched terms: {matched_terms}")
        print(f"Topics: {topics}")
        
        # Check if result matches expectation
        if is_relevant == test_case['expected_relevant']:
            print("✅ PASS")
        else:
            print("❌ FAIL")
        
        print("-" * 40)

if __name__ == "__main__":
    test_relevance_checking() 
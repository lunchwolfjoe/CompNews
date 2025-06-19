from typing import List, Dict
from processors.deduplicator import Deduplicator
from processors.summarizer import Summarizer
from processors.entity_extractor import EntityExtractor
import logging
import json

class ArticleProcessor:
    def __init__(self):
        self.deduplicator = Deduplicator()
        self.summarizer = Summarizer()
        self.entity_extractor = EntityExtractor()
        self.logger = logging.getLogger(self.__class__.__name__)

    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        processed = []
        
        # Step 1: Deduplicate and normalize articles
        self.logger.info(f"Starting deduplication of {len(articles)} articles")
        unique_articles = self.deduplicator.deduplicate(articles)
        self.logger.info(f"After deduplication: {len(unique_articles)} articles")
        
        for article in unique_articles:
            try:
                # Step 2: Summarize article
                summarized = self.summarizer.summarize(article)
                if not summarized:
                    self.logger.warning(f"Summarization failed for article: {article.get('title', 'Unknown')}")
                    continue
                
                # Step 3: Extract entities
                processed_article = self.entity_extractor.extract(summarized)
                if not processed_article:
                    self.logger.warning(f"Entity extraction failed for article: {article.get('title', 'Unknown')}")
                    continue
                
                # Step 4: Add relevance metadata
                if 'matched_terms' in article:
                    # Store matched terms as JSON string
                    processed_article['matched_terms'] = json.dumps(article['matched_terms'])
                    # Calculate relevance score based on number of unique matches
                    processed_article['relevance_score'] = len(set(article['matched_terms']))
                
                processed.append(processed_article)
                self.logger.info(f"Successfully processed article: {processed_article.get('title', 'Unknown')}")
                
            except Exception as e:
                self.logger.error(f"Error processing article {article.get('title', 'Unknown')}: {str(e)}")
                continue
        
        self.logger.info(f"Successfully processed {len(processed)} articles")
        return processed 
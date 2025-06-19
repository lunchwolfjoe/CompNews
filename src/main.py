from src.scrapers.guardian_scraper import GuardianScraper
from src.processors.pipeline import ArticleProcessor
from src.database.connection import get_db
from src.database.models import Article
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Scrape articles
    scraper = GuardianScraper()
    articles = scraper.scrape()
    logger.info(f"Scraped {len(articles)} articles")

    # Process articles
    processor = ArticleProcessor()
    processed_articles = processor.process_articles(articles)
    logger.info(f"Processed {len(processed_articles)} articles")

    # Store processed articles in the database
    with get_db() as db:
        for article_data in processed_articles:
            article = Article(**article_data)
            db.add(article)
        db.commit()
    logger.info("Articles stored in the database")

if __name__ == "__main__":
    main() 
from scrapers.guardian_scraper import GuardianScraper
import json

def main():
    scraper = GuardianScraper()
    articles = scraper.scrape()
    print(json.dumps(articles, indent=2, default=str))

if __name__ == "__main__":
    main() 
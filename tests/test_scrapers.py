import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from bs4 import BeautifulSoup

from src.scrapers.base_scraper import BaseScraper
from src.scrapers.bloomberg_scraper import BloombergScraper

class TestBaseScraper:
    @pytest.fixture
    def mock_scraper(self):
        class MockScraper(BaseScraper):
            def scrape(self):
                return [{"title": "Test Article"}]
                
            def parse_article(self, html_content):
                return {"title": "Test Article"}
        
        return MockScraper()

    def test_clean_text(self, mock_scraper):
        text = "  This   is   a   test   "
        cleaned = mock_scraper.clean_text(text)
        assert cleaned == "This is a test"

    def test_extract_date(self, mock_scraper):
        # Test with current date as placeholder
        date = mock_scraper.extract_date("2024-03-20")
        assert isinstance(date, datetime)

    def test_handle_error(self, mock_scraper):
        error = Exception("Test error")
        mock_scraper.handle_error(error, {"context": "test"})
        # Verify error was logged (we could add assertions here if we mock the logger)

class TestBloombergScraper:
    @pytest.fixture
    def scraper(self):
        return BloombergScraper()

    @pytest.fixture
    def mock_html(self):
        return """
        <html>
            <body>
                <h1 class="headline">Test Article</h1>
                <div class="body-copy">Test content</div>
                <time>2024-03-20</time>
                <span class="author">Test Author</span>
            </body>
        </html>
        """

    @patch('requests.get')
    def test_scrape_article(self, mock_get, scraper, mock_html):
        # Mock the response
        mock_response = Mock()
        mock_response.text = mock_html
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Test scraping
        result = scraper.scrape_article("https://test.com/article")
        
        assert result is not None
        assert result["title"] == "Test Article"
        assert result["content"] == "Test content"
        assert result["author"] == "Test Author"
        assert result["source"] == "Bloomberg"

    @patch('requests.get')
    def test_scrape_article_error(self, mock_get, scraper):
        # Mock a failed request
        mock_get.side_effect = Exception("Test error")
        
        # Test error handling
        result = scraper.scrape_article("https://test.com/article")
        assert result is None

    def test_parse_article(self, scraper, mock_html):
        result = scraper.parse_article(mock_html, "https://test.com/article")
        
        assert result is not None
        assert result["title"] == "Test Article"
        assert result["content"] == "Test content"
        assert result["author"] == "Test Author"
        assert result["source"] == "Bloomberg"

    def test_parse_article_missing_data(self, scraper):
        # Test with incomplete HTML
        html = "<html><body></body></html>"
        result = scraper.parse_article(html, "https://test.com/article")
        assert result is None

    @patch('requests.get')
    def test_rate_limiting(self, mock_get, scraper):
        # Mock successful responses
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Test that rate limiting is enforced
        start_time = datetime.now()
        scraper.scrape_article("https://test.com/article1")
        scraper.scrape_article("https://test.com/article2")
        end_time = datetime.now()

        # Verify that at least rate_limit seconds passed between requests
        assert (end_time - start_time).total_seconds() >= scraper.rate_limit 
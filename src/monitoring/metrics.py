from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from functools import wraps
from typing import Callable, Any
import logging

# Scraping metrics
SCRAPE_REQUESTS = Counter(
    'scraper_requests_total',
    'Total number of scraping requests',
    ['source', 'status']
)

SCRAPE_DURATION = Histogram(
    'scraper_request_duration_seconds',
    'Time spent scraping',
    ['source'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

SCRAPE_ERRORS = Counter(
    'scraper_errors_total',
    'Total number of scraping errors',
    ['source', 'error_type']
)

# Rate limiting metrics
RATE_LIMIT_DELAYS = Histogram(
    'scraper_rate_limit_delay_seconds',
    'Time spent waiting due to rate limiting',
    ['source'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# Database metrics
DB_CONNECTIONS = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Time spent executing database queries',
    ['operation'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

class MetricsCollector:
    def __init__(self, port: int = 8000):
        self.logger = logging.getLogger(__name__)
        start_http_server(port)
        self.logger.info(f"Metrics server started on port {port}")

    def track_scrape(self, source: str):
        """
        Decorator to track scraping metrics.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    SCRAPE_REQUESTS.labels(source=source, status='success').inc()
                    return result
                except Exception as e:
                    SCRAPE_REQUESTS.labels(source=source, status='error').inc()
                    SCRAPE_ERRORS.labels(source=source, error_type=type(e).__name__).inc()
                    raise
                finally:
                    duration = time.time() - start_time
                    SCRAPE_DURATION.labels(source=source).observe(duration)
            return wrapper
        return decorator

    def track_rate_limit(self, source: str, delay: float):
        """
        Track rate limiting delays.
        """
        RATE_LIMIT_DELAYS.labels(source=source).observe(delay)

    def track_db_operation(self, operation: str):
        """
        Decorator to track database operations.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    DB_CONNECTIONS.inc()
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    DB_QUERY_DURATION.labels(operation=operation).observe(duration)
                    DB_CONNECTIONS.dec()
            return wrapper
        return decorator 
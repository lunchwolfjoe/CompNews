from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=True)
    source = Column(String)  # Direct source name for simplicity
    url = Column(String(500), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    published_date = Column(DateTime)
    scraped_date = Column(DateTime, nullable=False)
    author = Column(String(200))
    category = Column(String, nullable=True)  # Changed from ARRAY to String (comma-separated categories)
    article_metadata = Column(Text, nullable=True)  # Changed from JSON to Text for SQLite compatibility
    entities = Column(Text)  # JSON string of extracted entities
    matched_terms = Column(JSON)  # JSON string of matched search terms
    relevance_score = Column(Float)  # Score based on contextual matches
    topics = Column(JSON)  # Store article topics as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Article(title='{self.title}', source='{self.source}', published='{self.published_date}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'url': self.url,
            'source': self.source,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'matched_terms': self.matched_terms,
            'topics': self.topics,
            'relevance_score': self.relevance_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    base_url = Column(String)
    config = Column(Text)  # Changed from JSON to Text for SQLite compatibility
    last_crawled = Column(DateTime)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
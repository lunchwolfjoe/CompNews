<<<<<<< HEAD
# CompNews
=======
# 📰 CompNews - Compensation News Aggregator

A comprehensive news aggregator focused on compensation, salary, and employment-related news from multiple sources. Built with Streamlit, Python, and SQLAlchemy.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Installation & Setup

1. **Clone the repository** (if not already done)
   ```bash
   git clone https://github.com/yourusername/compnews.git
   cd compnews
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install spaCy model** (required for text processing)
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

   Or use the startup script:
   ```bash
   python start_app.py
   ```

5. **Access the web interface**
   Open your browser and go to: http://localhost:8501

## 🎯 Features

### Current Implementation (MVP)
- ✅ **Multi-Source News Aggregation**: Collects articles from The Guardian, Associated Press, Google News, and Yahoo Finance
- ✅ **Smart Content Filtering**: Uses relevance scoring to identify compensation-related articles
- ✅ **Article Grouping**: Automatically groups similar articles to reduce redundancy
- ✅ **Interactive UI**: Clean, collapsible interface built with Streamlit
- ✅ **SQLite Database**: Local storage for articles
- ✅ **Streamlit Web UI**: Interactive web interface for browsing articles
- ✅ **Search & Filter**: Basic text search and date range filtering
- ✅ **Real-time Data Collection**: Scrape new articles directly from the UI

### Planned Features
- **Advanced NLP**: Sentiment analysis, trend detection, and categorization
- **Elasticsearch Integration**: Full-text search capabilities
- **Redis Caching**: Performance optimization
- **User Authentication**: Role-based access control
- **Analytics Dashboard**: Usage metrics and insights
- **Automated Scheduling**: Regular data collection

## 📊 Usage

### Scraping Articles
1. Open the web interface at http://localhost:8501
2. Click the **"🔄 Scrape New Articles"** button in the sidebar
3. Wait for the scraping process to complete
4. New articles will be automatically processed and stored

### Searching & Filtering
- **Search**: Use the search box to find articles by keywords
- **Date Range**: Filter articles by publication date
- **Real-time**: Results update automatically as you type

## 🏗️ Architecture

```
CompNews/
├── app.py                  # Main Streamlit application
├── start_app.py           # Application startup script
├── src/
│   ├── database/          # Database models and connection
│   ├── scrapers/          # Web scraping modules
│   ├── processors/        # Text processing pipeline
│   └── monitoring/        # Metrics and monitoring
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
```

## 🛠️ Technical Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.8+
- **Database**: SQLite (development), PostgreSQL (production)
- **Web Scraping**: BeautifulSoup, Selenium, Scrapy
- **NLP**: spaCy, transformers
- **Caching**: Redis (planned)
- **Search**: Elasticsearch (planned)
- **Deployment**: Docker, Docker Compose

## 📈 Development Status

**Phase 1: Foundation** ✅ **COMPLETED**
- Basic web scraper infrastructure
- Database setup and models
- Docker configuration
- Basic monitoring and metrics

**Phase 2: Core Processing** 🚧 **IN PROGRESS**
- ✅ Basic Streamlit UI (MVP)
- ✅ Article processing pipeline
- ⏳ Advanced NLP features
- ⏳ Redis queue system
- ⏳ Error handling improvements

**Phase 3: Search & UI** ⏳ **PLANNED**
- Elasticsearch integration
- Advanced filtering
- Performance optimization
- Enhanced UI/UX

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `REDIS_URL`: Redis connection string (when implemented)
- `ELASTICSEARCH_URL`: Elasticsearch endpoint (when implemented)

### Database Schema
The application uses the following main tables:
- `articles`: Stores scraped and processed articles
- `sources`: Manages news source configurations

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run specific test files:
```bash
pytest tests/test_scrapers.py -v
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Install spaCy model: `python -m spacy download en_core_web_sm`

**Database Errors**
- The application will create a SQLite database automatically
- For production, set `DATABASE_URL` environment variable

**Port Already in Use**
- Streamlit default port is 8501
- Use `--server.port XXXX` to specify a different port

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or issues, please open a GitHub issue or contact the development team.

---

**Status**: MVP Ready 🎉
**Last Updated**: December 2024
**Version**: 1.0.0 

## Live Demo

[Deployed on Streamlit Cloud](https://compnews.streamlit.app)

## Project Structure

```
CompNews/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore rules
├── src/
│   ├── database/
│   │   ├── connection.py # Database connection and setup
│   │   └── models.py     # SQLAlchemy models
│   ├── scrapers/
│   │   ├── base_scraper.py
│   │   ├── guardian_scraper.py
│   │   ├── ap_scraper.py
│   │   ├── google_news_scraper.py
│   │   └── yahoo_finance_scraper.py
│   └── processors/
│       ├── pipeline.py
│       ├── deduplicator.py
│       ├── entity_extractor.py
│       └── summarizer.py
└── tests/
    └── test_scrapers.py
```

## Configuration

### Search Terms
The app uses predefined search terms to identify relevant articles:
- compensation, salary, wage, pay gap, minimum wage
- equal pay, benefits, remuneration, bonus, payroll
- labor market, employment cost, income inequality

You can modify these in the Streamlit sidebar.

### Sources
Currently supported news sources:
- The Guardian (Business RSS)
- Associated Press (Business, Technology, Politics RSS)
- Google News (Business topics)
- Yahoo Finance (Market headlines)

## Deployment

### Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set the main file path to `app.py`
   - Deploy!

### Environment Variables

For production deployment, you may want to set these environment variables:
- `DATABASE_URL`: Database connection string
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

## Development

### Adding New Sources

1. Create a new scraper class in `src/scrapers/`
2. Inherit from `BaseScraper`
3. Implement the required methods
4. Add the source to the main app

### Database Migrations

The app automatically handles database migrations. If you need to add new fields:

1. Update the model in `src/database/models.py`
2. Add migration logic in `src/database/connection.py`
3. The app will automatically apply migrations on startup

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- News sources: The Guardian, Associated Press, Google News, Yahoo Finance
- Database: SQLite with SQLAlchemy ORM

## Support

If you encounter any issues or have questions, please open an issue on GitHub. 
>>>>>>> ffd94d6 (Initial commit: CompNews - Compensation News Aggregator with article grouping and multi-source scraping)

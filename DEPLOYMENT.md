# Deployment Guide - Streamlit Cloud

## Quick Deployment Steps

### 1. GitHub Setup
```bash
# Create a new repository on GitHub
# Then link your local repo:
git remote add origin https://github.com/YOUR_USERNAME/compnews.git
git branch -M main
git push -u origin main
```

### 2. Streamlit Cloud Deployment

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Configure your app:**
   - **Repository**: Select your `compnews` repository
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose your preferred URL (e.g., `compnews`)
5. **Click "Deploy"**

### 3. Environment Setup

The app will automatically:
- Install dependencies from `requirements.txt`
- Create the SQLite database
- Run database migrations
- Start the Streamlit server

### 4. Post-Deployment

- **First Run**: The app will take a few minutes to scrape initial articles
- **Database**: SQLite database is created automatically
- **Logs**: Check Streamlit Cloud logs for any issues

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are in `requirements.txt`
   - Check that import paths are correct

2. **Database Issues**
   - The app creates the database automatically
   - Check logs for migration errors

3. **Scraping Issues**
   - Some RSS feeds may be temporarily unavailable
   - The app will continue with available sources

### Performance Tips

- **Database**: SQLite is sufficient for small to medium scale
- **Caching**: Streamlit automatically caches expensive operations
- **Memory**: The app is optimized for Streamlit Cloud's memory limits

## Monitoring

- **Streamlit Cloud Dashboard**: Monitor app performance and logs
- **Database Size**: SQLite database grows with articles
- **Scraping Success**: Check logs for successful article collection

## Updates

To update your deployed app:
```bash
git add .
git commit -m "Update description"
git push origin main
```

Streamlit Cloud will automatically redeploy your app. 
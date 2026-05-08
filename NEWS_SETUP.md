# News API Setup Guide

## The Issue
The news function can work with or without a NewsAPI key. Without a key, it uses Google News as a fallback source.

## Option 1: Use NewsAPI (Recommended for better news)
1. Get a free API key from https://newsapi.org/
2. Add it to your `.env` file: `NEWS_API_KEY=your_actual_key_here`
3. The system will use NewsAPI for more comprehensive news coverage

## Option 2: Use Free Fallback (No API Key Required)
If you don't add a NewsAPI key, the system automatically uses Google News RSS feeds, which works without any API key.

## How to Test
Once set up (or without setup for fallback), run:
```bash
python -c "from utils import get_news; print(get_news(language='en'))"
```

You should see news headlines from either NewsAPI or Google News.
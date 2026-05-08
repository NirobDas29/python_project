# Weather API Setup Guide

## The Issue
The weather function requires a valid OpenWeatherMap API key to work. Currently, it's using a placeholder value.

## Solution: Add Your API Key

### Option 1: Use .env File (Recommended)
1. Copy `.env.example` to `.env`
2. Edit `.env` and replace `your_api_key_here` with your actual API key
3. Save the file

Your `.env` should look like:
```
OPENWEATHERMAP_API_KEY=abc123def456
```

### Option 2: Set Environment Variable (Windows PowerShell)
```powershell
$env:OPENWEATHERMAP_API_KEY="your_api_key_here"
```

To make it permanent:
```powershell
setx OPENWEATHERMAP_API_KEY "your_api_key_here"
```

### Option 3: Edit config.py Directly
Edit `config.py` line 5:
```python
WEATHER_API_KEY = "your_api_key_here"
```

## How to Get an API Key
1. Go to https://openweathermap.org/api
2. Sign up for a free account
3. Go to API keys section
4. Copy your API key
5. Add it using one of the methods above

## How to Test
Once you've added your key, run:
```bash
python -c "from utils import get_weather; print(get_weather(language='en', city='London'))"
```

You should see weather information instead of an error message.

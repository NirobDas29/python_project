import os
from pathlib import Path

ENV_FILE = Path(__file__).with_name(".env")

if ENV_FILE.exists():
    with open(ENV_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value

# ── API Keys ── Replace placeholders here OR add real keys to your .env file ─
OPENAI_API_KEY  = os.environ.get("OPENAI_API_KEY",  "<Your OpenAI Key Here>")
NEWS_API_KEY    = os.environ.get("NEWS_API_KEY",    "<Your NewsAPI Key Here>")
NEWS_API_URL    = os.environ.get("NEWS_API_URL",    "https://newsapi.org/v2/top-headlines")
WEATHER_API_KEY = os.environ.get(
    "OPENWEATHERMAP_API_KEY",
    os.environ.get(
        "OPENWEATHER_API_KEY",
        os.environ.get("WEATHER_API_KEY", "<Your OpenWeatherMap Key Here>")
    )
)
WEATHER_API_URL = os.environ.get(
    "OPENWEATHERMAP_API_URL",
    os.environ.get("OPENWEATHER_URL", "https://api.openweathermap.org/data/2.5/weather")
)

DEFAULT_LANGUAGE = "bn"
DEFAULT_CITY     = "Dhaka"

WAKE_WORD_EN = "jarvis"
WAKE_WORD_BN = "জার্ভিস"

MUSIC_LIBRARY = {
    "bohemian":     "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "shape of you": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
}

APPS = {
    "calculator":    "calc.exe",
    "notepad":       "notepad.exe",
    "file explorer": "explorer.exe",
    "chrome":        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vlc":           r"C:\Program Files\VideoLAN\VLC\vlc.exe",
}

TODO_FILE = "todos.json"
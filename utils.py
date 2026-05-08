import datetime
import json
import os
import random
import requests
import webbrowser

from config import WEATHER_API_KEY, WEATHER_API_URL, DEFAULT_CITY, TODO_FILE

CUSTOM_DATA_FILE = "custom_data.json"


def _load_custom_data():
    if os.path.exists(CUSTOM_DATA_FILE):
        try:
            with open(CUSTOM_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"websites": {}, "apps": {}, "music": {}}


def _save_custom_data(data):
    with open(CUSTOM_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_website(name, url, language="bn"):
    name = name.lower().strip()
    data = _load_custom_data()
    data["websites"][name] = url
    _save_custom_data(data)
    if language == "en":
        return f"Website \"{name}\" added. Now say: \"open {name}\""
    return f"\"{name}\" ওয়েবসাইট যোগ হয়েছে। এখন বলুন: \"{name} খুলুন\""


def list_websites(language="bn"):
    data = _load_custom_data()
    sites = data.get("websites", {})
    builtin = {
        "google":    "https://google.com",
        "youtube":   "https://youtube.com",
        "facebook":  "https://facebook.com",
        "linkedin":  "https://linkedin.com",
        "wikipedia": "https://wikipedia.org",
    }
    if language == "en":
        result = "Built-in Websites:\n"
        for name, url in builtin.items():
            result += f"  • {name}: {url}\n"
        if sites:
            result += "\nYour added websites:\n"
            for name, url in sites.items():
                result += f"  • {name}: {url}\n"
        else:
            result += "\n(No custom websites added yet)"
    else:
        result = "Built-in ওয়েবসাইট:\n"
        for name, url in builtin.items():
            result += f"  • {name}: {url}\n"
        if sites:
            result += "\nআপনার যোগ করা ওয়েবসাইট:\n"
            for name, url in sites.items():
                result += f"  • {name}: {url}\n"
        else:
            result += "\n(এখনো কোনো custom website যোগ করা হয়নি)"
    return result


def add_app(name, path, language="bn"):
    name = name.lower().strip()
    data = _load_custom_data()
    data["apps"][name] = path
    _save_custom_data(data)
    if language == "en":
        return f"App \"{name}\" added. Now say: \"open {name}\""
    return f"\"{name}\" অ্যাপ যোগ হয়েছে। এখন বলুন: \"{name} খুলুন\""


def list_apps(language="bn"):
    from config import APPS
    data = _load_custom_data()
    custom_apps = data.get("apps", {})
    if language == "en":
        result = "Built-in Apps:\n"
        for name in APPS:
            result += f"  • {name}\n"
        if custom_apps:
            result += "\nYour added apps:\n"
            for name, path in custom_apps.items():
                result += f"  • {name}: {path}\n"
        else:
            result += "\n(No custom apps added yet)"
    else:
        result = "Built-in অ্যাপ:\n"
        for name in APPS:
            result += f"  • {name}\n"
        if custom_apps:
            result += "\nআপনার যোগ করা অ্যাপ:\n"
            for name, path in custom_apps.items():
                result += f"  • {name}: {path}\n"
        else:
            result += "\n(এখনো কোনো custom অ্যাপ যোগ করা হয়নি)"
    return result


def add_music(name, url, language="bn"):
    name = name.lower().strip()
    data = _load_custom_data()
    data["music"][name] = url
    _save_custom_data(data)
    if language == "en":
        return f"Song \"{name}\" added. Now say: \"play {name}\""
    return f"\"{name}\" গান যোগ হয়েছে। এখন বলুন: \"গান বাজাও {name}\""


def list_music(language="bn"):
    from config import MUSIC_LIBRARY
    data = _load_custom_data()
    custom_music = data.get("music", {})
    if language == "en":
        result = "Built-in music:\n"
        for name in MUSIC_LIBRARY:
            result += f"  • {name}\n"
        if custom_music:
            result += "\nYour added music:\n"
            for name, url in custom_music.items():
                result += f"  • {name}: {url}\n"
        else:
            result += "\n(No custom music added yet)"
    else:
        result = "Built-in গান:\n"
        for name in MUSIC_LIBRARY:
            result += f"  • {name}\n"
        if custom_music:
            result += "\nআপনার যোগ করা গান:\n"
            for name, url in custom_music.items():
                result += f"  • {name}: {url}\n"
        else:
            result += "\n(এখনো কোনো custom গান যোগ করা হয়নি)"
    return result


def open_app(app_name, language="bn"):
    import subprocess
    from config import APPS

    app_key = app_name.lower().strip()

    if app_key in APPS:
        try:
            subprocess.Popen(APPS[app_key])
            return f"Opening {app_name}..." if language == "en" else f"\"{app_name}\" খোলা হচ্ছে।"
        except Exception as e:
            return f"Failed to open {app_name}: {e}" if language == "en" \
                   else f"\"{app_name}\" খুলতে পারলাম না: {e}"

    data = _load_custom_data()
    custom_apps = data.get("apps", {})
    if app_key in custom_apps:
        try:
            subprocess.Popen(custom_apps[app_key], shell=True)
            return f"Opening {app_name}..." if language == "en" else f"\"{app_name}\" খোলা হচ্ছে।"
        except Exception as e:
            return f"Failed to open {app_name}: {e}" if language == "en" \
                   else f"\"{app_name}\" খুলতে পারলাম না: {e}"

    all_apps = list(APPS.keys()) + list(custom_apps.keys())
    available = ", ".join(all_apps)
    return f"App \"{app_name}\" not found. Available: {available}" if language == "en" \
           else f"\"{app_name}\" চেনা গেলো না। পাওয়া আছে: {available}"


def get_time(language="bn"):
    now = datetime.datetime.now()
    hour   = now.strftime("%I").lstrip("0") or "12"
    minute = now.strftime("%M")
    period = "সকাল" if now.hour < 12 else ("দুপুর" if now.hour < 17 else ("বিকেল" if now.hour < 20 else "সন্ধ্যা"))

    if language == "bn":
        return f"এখন সময় {period} {hour}টা {minute} মিনিট।"
    else:
        am_pm = now.strftime("%p")
        return f"The current time is {hour}:{minute} {am_pm}."


def get_date(language="bn"):
    now = datetime.datetime.now()
    if language == "bn":
        bangla_months = [
            "জানুয়ারি", "ফেব্রুয়ারি", "মার্চ", "এপ্রিল",
            "মে", "জুন", "জুলাই", "আগস্ট",
            "সেপ্টেম্বর", "অক্টোবর", "নভেম্বর", "ডিসেম্বর"
        ]
        bangla_days = ["সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার",
                       "শুক্রবার", "শনিবার", "রবিবার"]
        day_name = bangla_days[now.weekday()]
        month    = bangla_months[now.month - 1]
        return f"আজ {day_name}, {now.day} {month} {now.year}।"
    else:
        return now.strftime("Today is %A, %B %d, %Y.")


def get_weather(language="bn", city=None):
    city = city or DEFAULT_CITY
    if not WEATHER_API_KEY or WEATHER_API_KEY == "<Your OpenWeatherMap Key Here>":
        return "Please add your OpenWeatherMap API key in config.py (WEATHER_API_KEY), set OPENWEATHERMAP_API_KEY / OPENWEATHER_API_KEY / WEATHER_API_KEY in your environment, or add it to a .env file." if language == "en" \
               else "আবহাওয়া জানতে config.py-তে WEATHER_API_KEY-এ বা পরিবেশে OPENWEATHERMAP_API_KEY / OPENWEATHER_API_KEY / WEATHER_API_KEY-এ OpenWeatherMap API key দিন, অথবা .env ফাইলে যোগ করুন।"
    try:
        lang_param = "bn" if language == "bn" else "en"
        url = f"{WEATHER_API_URL}?q={city}&appid={WEATHER_API_KEY}&units=metric&lang={lang_param}"
        r   = requests.get(url, timeout=5)
        if r.status_code == 200:
            data        = r.json()
            temp        = data["main"]["temp"]
            humidity    = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            if language == "en":
                return f"Weather in {city}: Temperature {temp}°C, Humidity {humidity}%, Condition: {description}."
            return f"{city} এর আবহাওয়া: তাপমাত্রা {temp}°C, আর্দ্রতা {humidity}%, অবস্থা: {description}।"
        if r.status_code == 401:
            return "OpenWeatherMap API key is invalid. Please check your key and try again." if language == "en" else "OpenWeatherMap API keyটি সঠিক নয়। অনুগ্রহ করে ঠিক করে আবার চেষ্টা করুন।"
        return "Could not fetch weather data." if language == "en" else "আবহাওয়া তথ্য পেতে পারেনি।"
    except requests.exceptions.ConnectionError:
        return "No internet connection." if language == "en" else "Internet সংযোগ নেই।"
    except Exception as e:
        return f"Error: {e}" if language == "en" else f"ত্রুটি: {e}"


JOKES_BN = [
    "একজন প্রোগ্রামার রেস্তোরাঁয় গেলেন। ওয়েটার জিজ্ঞেস করলেন — টেবিল কতজনের? প্রোগ্রামার বললেন — এটা কি একটা বুলিয়ান ভেলু নাকি?",
    "আমার ঘড়ি বলছে এখন তিনটা। কিন্তু আমার মাথা বলছে এখন ঘুমানোর সময়।",
    "একজন শিক্ষক বলেছেন — যারা পরীক্ষায় ফেল করেছ তারা হাত তুলুন। কেউ হাত তুললেন না। শিক্ষক বলেছেন — তাহলে কেউ পরীক্ষাও দেননি মনে হচ্ছে।",
    "Python শিখছি। এখন পর্যন্ত শুধু শিখেছি কীভাবে error বার্তা পড়তে হয়।",
    "একটা মাছ বলেছে অন্য মাছকে — তুমি কী করো? অন্য মাছ বলেছে — আমি অনলাইনে সময় কাটাই। জানো তো, মাছেরা সবসময় নেট এ থাকি।"
]

JOKES_EN = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "A SQL query walks into a bar, walks up to two tables and asks — Can I join you?",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "I'm reading a book about anti-gravity. It's impossible to put down."
]


def get_joke(language="bn"):
    return random.choice(JOKES_BN) if language == "bn" else random.choice(JOKES_EN)


def _load_todos():
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def _save_todos(todos):
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def add_todo(task, language="bn"):
    todos = _load_todos()
    entry = {
        "id":   len(todos) + 1,
        "task": task,
        "done": False,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    todos.append(entry)
    _save_todos(todos)
    return f"Task added: \"{task}\"" if language == "en" else f"কাজ যোগ করা হয়েছে: \"{task}\""


def list_todos(language="bn"):
    todos = _load_todos()
    if not todos:
        return "No tasks found." if language == "en" else "কোনো কাজ নেই।"
    result = "Your task list:\n" if language == "en" else "আপনার কাজের তালিকা:\n"
    for t in todos:
        status = "✅" if t["done"] else "⬜"
        result += f"  {status} {t['id']}. {t['task']}\n"
    return result


def complete_todo(task_id, language="bn"):
    todos = _load_todos()
    for t in todos:
        if t["id"] == task_id:
            t["done"] = True
            _save_todos(todos)
            return f"Task completed: \"{t['task']}\"" if language == "en" \
                   else f"কাজ সম্পন্ন করা হয়েছে: \"{t['task']}\""
    return "Task not found." if language == "en" else "এই নম্বরের কাজ পাওয়া গেলো না।"


def clear_todos(language="bn"):
    _save_todos([])
    return "All tasks cleared." if language == "en" else "সব কাজ মুছে ফেলা হয়েছে।"


def open_website(url, language="bn"):
    try:
        webbrowser.open(url)
        name = url.replace("https://", "").replace("http://", "").split("/")[0]
        return f"Opening {name}..." if language == "en" else f"\"{name}\" খোলা হচ্ছে।"
    except Exception as e:
        return f"Failed to open: {e}" if language == "en" else f"খুলতে পারলাম না: {e}"


def get_news(language="bn"):
    from config import NEWS_API_KEY, NEWS_API_URL
    if not NEWS_API_KEY or NEWS_API_KEY == "<Your NewsAPI Key Here>":
        # Fallback to free news source when no API key is provided
        return _get_news_fallback(language)
    try:
        country = "bd" if language == "bn" else "us"
        url = f"{NEWS_API_URL}?country={country}&apiKey={NEWS_API_KEY}"
        r   = requests.get(url, timeout=5)
        if r.status_code == 200:
            articles = r.json().get("articles", [])
            if not articles:
                return "No news found." if language == "en" else "এখন খবর পাওয়া গেলো না।"
            news_text = "Today's news:\n" if language == "en" else "আজকের খবর:\n"
            for i, article in enumerate(articles[:3], 1):
                news_text += f"{i}. {article['title']}\n"
            return news_text
        return "Could not fetch news." if language == "en" else "খবর পেতে পারেনি।"
    except requests.exceptions.ConnectionError:
        return "No internet connection." if language == "en" else "Internet সংযোগ নেই।"
    except Exception as e:
        return f"Error: {e}" if language == "en" else f"ত্রুটি: {e}"


def _get_news_fallback(language="bn"):
    """Fallback news function using free sources when no API key is available."""
    try:
        import xml.etree.ElementTree as ET

        # Using Google News RSS feed as fallback
        rss_url = f"https://news.google.com/rss?hl={'bn' if language == 'bn' else 'en'}&gl={'BD' if language == 'bn' else 'US'}&ceid={'BD:en' if language == 'bn' else 'US:en'}"

        r = requests.get(rss_url, timeout=10)
        if r.status_code != 200:
            return "Could not fetch news from fallback source." if language == "en" else "ফলব্যাক সোর্স থেকে খবর পেতে পারেনি।"

        # Parse the RSS XML
        root = ET.fromstring(r.content)
        items = root.findall('.//item')

        if not items:
            return "No news available from fallback source." if language == "en" else "ফলব্যাক সোর্স থেকে খবর পাওয়া গেল না।"

        news_text = "Latest news (Google News):\n" if language == "en" else "সর্বশেষ খবর (Google News):\n"
        for i, item in enumerate(items[:3], 1):
            title_elem = item.find('title')
            if title_elem is not None:
                title = title_elem.text
                # Clean up the title (remove source info that Google adds)
                if " - " in title:
                    title = title.split(" - ")[0]
                news_text += f"{i}. {title}\n"

        return news_text

    except Exception as e:
        return f"Fallback news error: {e}" if language == "en" else f"ফলব্যাক খবর ত্রুটি: {e}"
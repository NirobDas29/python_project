import webbrowser
import re
from config import MUSIC_LIBRARY
from utils import (
    get_time, get_date, get_weather, get_joke,
    add_todo, list_todos, complete_todo, clear_todos,
    open_website, open_app, get_news,
    add_website, add_music, add_app,
    list_websites, list_music, list_apps
)


class CommandProcessor:
    def __init__(self, language="bn"):
        self.language = language

    def set_language(self, lang):
        self.language = lang

    def process(self, command):
        cmd = command.lower().strip()
        lang = self.language

        if self._match(cmd, ["সময়", "কত টা", "কতটা", "time", "what time"]):
            return get_time(lang)

        if self._match(cmd, ["তারিখ", "আজ কি দিন", "কি তারিখ", "date", "what date", "what day"]):
            return get_date(lang)

        if self._match(cmd, ["আবহাওয়া", "ওয়েদার", "তাপমাত্রা", "weather", "temperature"]):
            return get_weather(lang)

        if self._match(cmd, ["মজার কথা", "জোক", "হাসি", "joke", "tell a joke", "funny"]):
            return get_joke(lang)

        if self._match(cmd, ["খবর", "আজকের খবর", "news", "today news"]):
            return get_news(lang)

        if self._match(cmd, ["গান বাজাও", "গান চালাও", "play", "গান"]) and \
           not self._match(cmd, ["গান যোগ", "add music", "add song", "গান যোগ করো", "গান যোগ করুন"]):
            return self._play_music(cmd)

        if self._match(cmd, ["ওয়েবসাইট যোগ", "সাইট যোগ", "add website", "add site"]):
            return self._handle_add_website(cmd)

        if self._match(cmd, ["অ্যাপ যোগ", "app যোগ", "add app"]):
            return self._handle_add_app(cmd)

        if self._match(cmd, ["গান যোগ", "মিউজিক যোগ", "add music", "add song"]):
            return self._handle_add_music(cmd)

        if self._match(cmd, ["ওয়েবসাইট তালিকা", "সাইট লিস্ট", "list websites", "show websites"]):
            return list_websites(lang)

        if self._match(cmd, ["অ্যাপ তালিকা", "app লিস্ট", "list apps", "show apps"]):
            return list_apps(lang)

        if self._match(cmd, ["গানের তালিকা", "মিউজিক লিস্ট", "list music", "show music"]):
            return list_music(lang)

        if self._match(cmd, ["গুগল খুলুন", "গুগল খোলো", "open google", "google"]):
            return open_website("https://google.com", lang)

        if self._match(cmd, ["ইউটিউব খুলুন", "ইউটিউব খোলো", "open youtube", "youtube"]):
            return open_website("https://youtube.com", lang)

        if self._match(cmd, ["ফেসবুক খুলুন", "ফেসবুক খোলো", "open facebook", "facebook"]):
            return open_website("https://facebook.com", lang)

        if self._match(cmd, ["লিংকডইন", "open linkedin", "linkedin"]):
            return open_website("https://linkedin.com", lang)

        if self._match(cmd, ["উইকিপিডিয়া", "wikipedia"]):
            return open_website("https://wikipedia.org", lang)

        custom_open = self._try_open_custom_website(cmd, lang)
        if custom_open:
            return custom_open

        if self._match(cmd, ["ক্যালকুলেটর", "calculator"]):
            return open_app("calculator", lang)

        if self._match(cmd, ["নোটপ্যাড", "notepad"]):
            return open_app("notepad", lang)

        if self._match(cmd, ["ফাইল এক্সপ্লোরার", "ফোল্ডার", "file explorer", "explorer"]):
            return open_app("file explorer", lang)

        if self._match(cmd, ["ক্রোম", "chrome"]):
            return open_app("chrome", lang)

        if self._match(cmd, ["ভিএলসি", "vlc", "মিডিয়া প্লেয়ার"]):
            return open_app("vlc", lang)

        custom_app = self._try_open_custom_app(cmd, lang)
        if custom_app:
            return custom_app

        if self._match(cmd, ["কাজ যোগ করুন", "কাজ যোগ", "কাজ যোগ করো", "add task", "add todo"]):
            return self._handle_add_todo(cmd)

        if self._match(cmd, ["কাজের তালিকা", "কাজ দেখুন", "কাজ দেখো", "list tasks", "show tasks", "todo list"]):
            return list_todos(lang)

        if self._match(cmd, ["কাজ শেষ করুন", "কাজ সম্পন্ন", "complete task", "done task"]):
            return self._handle_complete_todo(cmd)

        if self._match(cmd, ["সব কাজ মুছুন", "কাজ মুছুন", "clear tasks", "clear todos"]):
            return clear_todos(lang)

        if self._match(cmd, ["বাংলা", "bangla", "bengali"]):
            self.language = "bn"
            return "ভাষা বাংলায় পরিবর্তিত হয়েছে।"

        if self._match(cmd, ["ইংলিশ", "english"]):
            self.language = "en"
            return "Language changed to English."

        if self._match(cmd, ["সাহায্য", "কী করতে পার", "help", "what can you do"]):
            return self._get_help()

        if self._match(cmd, ["বাই", "বিদায়", "বন্ধ করুন", "বন্ধ করো", "bye", "exit", "quit", "shutdown"]):
            return "__QUIT__"

        if lang == "bn":
            return "এটা আমি বুঝতে পারছি না। \"সাহায্য\" বলুন দেখুন কী করতে পার।"
        else:
            return "I don't understand that. Say \"help\" to see what I can do."

    def _match(self, cmd, keywords):
        return any(kw in cmd for kw in keywords)

    def _play_music(self, cmd):
        for keyword in ["play ", "গান বাজাও ", "গান চালাও "]:
            if keyword in cmd:
                song_name = cmd.split(keyword)[-1].strip()
                break
        else:
            song_name = ""

        for key, link in MUSIC_LIBRARY.items():
            if key in song_name or song_name in key:
                webbrowser.open(link)
                return f"Playing \"{key}\"..." if self.language == "en" else f"\"{key}\" বাজাচ্ছি।"

        from utils import _load_custom_data
        data = _load_custom_data()
        for key, link in data.get("music", {}).items():
            if key in song_name or song_name in key:
                webbrowser.open(link)
                return f"Playing \"{key}\"..." if self.language == "en" else f"\"{key}\" বাজাচ্ছি।"

        if not song_name:
            import random
            all_music = {**MUSIC_LIBRARY, **data.get("music", {})}
            if all_music:
                key = random.choice(list(all_music.keys()))
                webbrowser.open(all_music[key])
                return f"Playing \"{key}\"..." if self.language == "en" else f"\"{key}\" বাজাচ্ছি।"
            return "Music library is empty." if self.language == "en" else "গানের তালিকা খালি।"

        all_music = {**MUSIC_LIBRARY, **data.get("music", {})}
        available = ", ".join(all_music.keys())
        return f"\"{song_name}\" not found. Available: {available}" if self.language == "en" \
               else f"\"{song_name}\" পাওয়া গেলো না। পাওয়া আছে: {available}"

    def _handle_add_website(self, cmd):
        url_match = re.search(r'https?://\S+', cmd)
        if not url_match:
            return "Format: \"add website youtube link https://youtube.com\"" if self.language == "en" \
                   else "ফরম্যাট: \"ওয়েবসাইট যোগ করো youtube লিংক https://youtube.com\""

        url = url_match.group()
        for kw in ["ওয়েবসাইট যোগ করো ", "সাইট যোগ করো ", "ওয়েবসাইট যোগ ", "add website ", "add site "]:
            if kw in cmd:
                after = cmd.split(kw)[-1]
                name = re.split(r'\s+লিংক\s+|\s+link\s+', after)[0].strip()
                break
        else:
            name = url.split("//")[-1].split("/")[0]

        if not name:
            name = url.split("//")[-1].split("/")[0]

        return add_website(name, url, self.language)

    def _handle_add_app(self, cmd):
        for kw in ["অ্যাপ যোগ করো ", "app যোগ করো ", "অ্যাপ যোগ ", "add app "]:
            if kw in cmd:
                after = cmd.split(kw)[-1].strip()
                parts = re.split(r'\s+পাথ\s+|\s+path\s+', after, maxsplit=1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    path = parts[1].strip()
                    return add_app(name, path, self.language)
                break

        return "Format: \"add app vlc path vlc.exe\"" if self.language == "en" \
               else "ফরম্যাট: \"অ্যাপ যোগ করো vlc পাথ vlc.exe\""

    def _handle_add_music(self, cmd):
        url_match = re.search(r'https?://\S+', cmd)
        if not url_match:
            return "Format: \"add music bohemian link https://youtube.com/...\"" if self.language == "en" \
                   else "ফরম্যাট: \"গান যোগ করো bohemian লিংক https://youtube.com/...\""

        url = url_match.group()
        for kw in ["গান যোগ করো ", "মিউজিক যোগ করো ", "গান যোগ ", "add music ", "add song "]:
            if kw in cmd:
                after = cmd.split(kw)[-1]
                name = re.split(r'\s+লিংক\s+|\s+link\s+', after)[0].strip()
                break
        else:
            name = "untitled"

        return add_music(name, url, self.language)

    def _try_open_custom_website(self, cmd, lang):
        from utils import _load_custom_data
        data = _load_custom_data()
        for name, url in data.get("websites", {}).items():
            if name.lower() in cmd:
                return open_website(url, lang)
        return None

    def _try_open_custom_app(self, cmd, lang):
        from utils import _load_custom_data
        data = _load_custom_data()
        for name, path in data.get("apps", {}).items():
            if name.lower() in cmd:
                return open_app(name, lang)
        return None

    def _handle_add_todo(self, cmd):
        for keyword in ["কাজ যোগ করুন ", "কাজ যোগ করো ", "কাজ যোগ ", "add task ", "add todo "]:
            if keyword in cmd:
                task = cmd.split(keyword)[-1].strip()
                if task:
                    return add_todo(task, self.language)
        return "What task to add?" if self.language == "en" else "কী কাজ যোগ করবেন বলুন।"

    def _handle_complete_todo(self, cmd):
        numbers = re.findall(r'\d+', cmd)
        if numbers:
            return complete_todo(int(numbers[0]), self.language)
        return "Which task number to complete?" if self.language == "en" \
               else "কোন নম্বরের কাজ সম্পন্ন করবেন বলুন।"

    def _get_help(self):
        if self.language == "bn":
            return (
                "আমি এই কাজগুলো করতে পার:\n"
                "• সময় ও তারিখ জানান\n"
                "• আবহাওয়া জানান\n"
                "• মজার কথা বলুন\n"
                "• খবর শুনুন\n"
                "• গান বাজান\n"
                "• ওয়েবসাইট খুলুন (গুগল, ইউটিউব, ফেসবুক)\n"
                "• অ্যাপ খুলুন (ক্যালকুলেটর, নোটপ্যাড)\n"
                "• কাজের তালিকা পরিচালনা করুন\n"
                "• ভাষা বদলান (বাংলা / ইংলিশ)\n\n"
                "── নতুন যোগ করুন ──\n"
                "• \"ওয়েবসাইট যোগ করো [নাম] লিংক [url]\"\n"
                "• \"অ্যাপ যোগ করো [নাম] পাথ [path]\"\n"
                "• \"গান যোগ করো [নাম] লিংক [url]\"\n"
                "• \"ওয়েবসাইট তালিকা\" / \"গানের তালিকা\" / \"অ্যাপ তালিকা\""
            )
        else:
            return (
                "I can do these things:\n"
                "• Tell time and date\n"
                "• Show weather\n"
                "• Tell jokes\n"
                "• Read news\n"
                "• Play music\n"
                "• Open websites (Google, YouTube, Facebook)\n"
                "• Open apps (Calculator, Notepad)\n"
                "• Manage to-do list\n"
                "• Switch language (English / Bangla)\n\n"
                "── Add new items ──\n"
                "• \"add website [name] link [url]\"\n"
                "• \"add app [name] path [path]\"\n"
                "• \"add music [name] link [url]\"\n"
                "• \"list websites\" / \"list music\" / \"list apps\""
            )
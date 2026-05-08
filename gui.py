import customtkinter as ctk
import tkinter as tk
import threading
import time
import math
import json
import os
from datetime import datetime
from threading import Lock

from speech_input  import SpeechInput
from speech_output import SpeechOutput
from commands      import CommandProcessor
from config        import WAKE_WORD_EN, WAKE_WORD_BN, DEFAULT_LANGUAGE
from utils         import add_website, add_music, add_app

BG       = "midnightblue"
WHITE    = "white"
BLUE     = "royalblue"
BLUE_LT  = "lightsteelblue"
TEXT     = "white"
TEXT_SM  = "lightgray"
GREEN    = "mediumseagreen"
ORANGE   = "darkorange"
RED      = "crimson"
PANEL_BG = "darkslateblue"
BORDER   = "steelblue"

USER_COLOR   = "deepskyblue"
JARVIS_COLOR = "lightyellow"
SYSTEM_COLOR = "lightgreen"
WARN_COLOR   = "darkorange"

HISTORY_FILE = "search_history.json"


class JarvisGUI:
    def __init__(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Jarvis — Voice Assistant")
        self.root.geometry("560x700")
        self.root.minsize(480, 600)
        self.root.configure(fg_color=BG)
        self.root.resizable(True, True)

        self.language      = DEFAULT_LANGUAGE
        self.speech_input  = SpeechInput(self.language)
        self.speech_output = SpeechOutput(self.language)
        self.command_proc  = CommandProcessor(self.language)

        self.is_listening  = False
        self.is_active     = False
        self.running       = True
        self.pulse_angle   = 0

        self.add_panel_visible     = False
        self.history_panel_visible = False

        self.state_lock = Lock()
        self.search_history = self._load_history()

        self._build_ui()
        self._start_wake_word_listener()
        self._animate()

    def _build_ui(self):
        self.top_bar = ctk.CTkFrame(self.root, fg_color="white", corner_radius=0, height=54)
        self.top_bar.pack(fill="x")
        self.top_bar.pack_propagate(False)
        top = self.top_bar

        ctk.CTkLabel(
            top, text="Jarvis Shobdo",
            font=("Segoe UI", 16, "bold"), text_color="navy"
        ).pack(side="left", padx=18)

        self.add_btn = ctk.CTkButton(
            top, text="➕ যোগ করুন", width=110, height=30,
            fg_color="honeydew", hover_color="palegreen",
            text_color="seagreen", font=("Segoe UI", 11, "bold"),
            command=self._toggle_add_panel, corner_radius=15
        )
        self.add_btn.pack(side="right", padx=6)

        self.history_btn = ctk.CTkButton(
            top, text="🕐 ইতিহাস", width=100, height=30,
            fg_color="lightyellow", hover_color="lemonchiffon",
            text_color="saddlebrown", font=("Segoe UI", 11, "bold"),
            command=self._toggle_history_panel, corner_radius=15
        )
        self.history_btn.pack(side="right", padx=6)

        self.lang_btn = ctk.CTkButton(
            top, text="🇧🇩 BN", width=72, height=30,
            fg_color="lightsteelblue", hover_color="powderblue",
            text_color="royalblue", font=("Segoe UI", 11, "bold"),
            command=self._toggle_language, corner_radius=15
        )
        self.lang_btn.pack(side="right", padx=6)

        self.add_panel = ctk.CTkFrame(self.root, fg_color=PANEL_BG, corner_radius=0)
        self._build_add_panel()

        self.history_panel = ctk.CTkFrame(self.root, fg_color="darkslateblue", corner_radius=0)
        self._build_history_panel()

        mid = ctk.CTkFrame(self.root, fg_color=BG)
        mid.pack(fill="x", pady=(16, 4))

        self.canvas = tk.Canvas(mid, width=120, height=120, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.status_label = ctk.CTkLabel(
            mid,
            text='অপেক্ষা করছি... "জার্ভিস" বলুন',
            font=("Segoe UI", 12), text_color=TEXT_SM
        )
        self.status_label.pack(pady=(4, 0))

        box = ctk.CTkFrame(self.root, fg_color="slategray", corner_radius=12)
        box.pack(fill="both", expand=True, padx=16, pady=10)

        ctk.CTkLabel(
            box, text="Conversation",
            font=("Segoe UI", 11, "bold"), text_color=TEXT_SM, anchor="w"
        ).pack(anchor="w", padx=14, pady=(10, 2))

        scroll = ctk.CTkScrollableFrame(box, fg_color="midnightblue", corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.output_text = tk.Text(
            scroll, wrap="word", font=("Segoe UI", 12),
            bg="midnightblue", fg="white", relief="flat",
            padx=10, pady=8, state="disabled", cursor="arrow"
        )
        self.output_text.pack(fill="both", expand=True)

        bot = ctk.CTkFrame(self.root, fg_color="white", corner_radius=0, height=60)
        bot.pack(fill="x")
        bot.pack_propagate(False)

        self.mic_btn = ctk.CTkButton(
            bot, text="🎙  কথা বলুন", width=160, height=38,
            fg_color="royalblue", hover_color="mediumblue",
            text_color="white", font=("Segoe UI", 13, "bold"),
            command=self._manual_listen, corner_radius=20
        )
        self.mic_btn.pack(pady=10)

    def _build_add_panel(self):
        title_row = ctk.CTkFrame(self.add_panel, fg_color="transparent")
        title_row.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            title_row, text="➕  নতুন যোগ করুন",
            font=("Segoe UI", 13, "bold"), text_color=WHITE
        ).pack(side="left")

        ctk.CTkButton(
            title_row, text="✕", width=28, height=28,
            fg_color="transparent", hover_color=BORDER,
            text_color=TEXT_SM, font=("Segoe UI", 13),
            command=self._toggle_add_panel, corner_radius=14
        ).pack(side="right")

        self.add_tab = tk.StringVar(value="website")

        tab_row = ctk.CTkFrame(self.add_panel, fg_color=BORDER, corner_radius=10)
        tab_row.pack(fill="x", padx=16, pady=(0, 10))

        tabs = [
            ("🌐 ওয়েবসাইট", "website"),
            ("💻 অ্যাপ",     "app"),
            ("🎵 গান",       "music"),
        ]
        for label, val in tabs:
            ctk.CTkRadioButton(
                tab_row, text=label, variable=self.add_tab, value=val,
                font=("Segoe UI", 11, "bold"), text_color=WHITE,
                fg_color=BLUE, border_color=BLUE_LT,
                command=self._on_tab_change
            ).pack(side="left", padx=14, pady=8)

        self.fields_frame = ctk.CTkFrame(self.add_panel, fg_color="transparent")
        self.fields_frame.pack(fill="x", padx=16, pady=(0, 4))

        ctk.CTkLabel(
            self.fields_frame, text="নাম / Name",
            font=("Segoe UI", 11), text_color=TEXT_SM
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.name_entry = ctk.CTkEntry(
            self.fields_frame,
            placeholder_text="যেমন: twitter, spotify, despacito",
            width=340, height=34,
            font=("Segoe UI", 12),
            fg_color=BORDER, border_color=BLUE,
            text_color=WHITE
        )
        self.name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.second_label = ctk.CTkLabel(
            self.fields_frame, text="লিংক / URL",
            font=("Segoe UI", 11), text_color=TEXT_SM
        )
        self.second_label.grid(row=2, column=0, sticky="w", pady=(0, 2))

        self.second_entry = ctk.CTkEntry(
            self.fields_frame,
            placeholder_text="https://twitter.com",
            width=340, height=34,
            font=("Segoe UI", 12),
            fg_color=BORDER, border_color=BLUE,
            text_color=WHITE
        )
        self.second_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        self.fields_frame.columnconfigure(0, weight=1)

        self.save_btn = ctk.CTkButton(
            self.add_panel,
            text="✅  সেভ করুন",
            width=180, height=36,
            fg_color="mediumseagreen", hover_color="seagreen",
            text_color="white", font=("Segoe UI", 12, "bold"),
            command=self._save_item, corner_radius=18
        )
        self.save_btn.pack(pady=(0, 14))

        self.feedback_label = ctk.CTkLabel(
            self.add_panel, text="",
            font=("Segoe UI", 11), text_color=GREEN
        )
        self.feedback_label.pack(pady=(0, 8))

    def _on_tab_change(self):
        tab = self.add_tab.get()
        self.name_entry.delete(0, "end")
        self.second_entry.delete(0, "end")
        self.feedback_label.configure(text="")

        if tab == "website":
            self.second_label.configure(text="লিংক / URL")
            self.name_entry.configure(placeholder_text="যেমন: twitter, github")
            self.second_entry.configure(placeholder_text="https://twitter.com")
        elif tab == "app":
            self.second_label.configure(text="পাথ / Path (.exe)")
            self.name_entry.configure(placeholder_text="যেমন: spotify, word")
            self.second_entry.configure(placeholder_text="C:\\Users\\...\\Spotify.exe  বা  notepad.exe")
        elif tab == "music":
            self.second_label.configure(text="লিংক / URL (YouTube)")
            self.name_entry.configure(placeholder_text="যেমন: despacito, আমার সোনার বাংলা")
            self.second_entry.configure(placeholder_text="https://youtube.com/watch?v=...")

    def _save_item(self):
        tab    = self.add_tab.get()
        name   = self.name_entry.get().strip()
        second = self.second_entry.get().strip()

        if not name or not second:
            self.feedback_label.configure(text="⚠️ নাম ও লিংক/পাথ দুটোই দিন।", text_color=ORANGE)
            return

        lang = self.language

        if tab == "website":
            if not second.startswith("http"):
                self.feedback_label.configure(text="⚠️ URL https:// দিয়ে শুরু করুন।", text_color=ORANGE)
                return
            result = add_website(name, second, lang)
        elif tab == "app":
            result = add_app(name, second, lang)
        elif tab == "music":
            if not second.startswith("http"):
                self.feedback_label.configure(text="⚠️ URL https:// দিয়ে শুরু করুন।", text_color=ORANGE)
                return
            result = add_music(name, second, lang)

        self.feedback_label.configure(text=result, text_color="mediumseagreen")
        self._add_output(f"➕ {result}", color="mediumseagreen")
        self.name_entry.delete(0, "end")
        self.second_entry.delete(0, "end")
        self.root.after(3000, lambda: self.feedback_label.configure(text=""))

    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.search_history[-100:], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"History save error: {e}")

    def _add_to_history(self, command, response):
        entry = {
            "command":  command,
            "response": response,
            "time":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.search_history.append(entry)
        self._save_history()
        if self.history_panel_visible:
            self.root.after(0, self._refresh_history_list)

    def _build_history_panel(self):
        title_row = ctk.CTkFrame(self.history_panel, fg_color="transparent")
        title_row.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            title_row, text="🕐  আগের কমান্ড",
            font=("Segoe UI", 13, "bold"), text_color=WHITE
        ).pack(side="left")

        ctk.CTkButton(
            title_row, text="🗑 মুছুন", width=72, height=26,
            fg_color="darkred", hover_color="firebrick",
            text_color="white", font=("Segoe UI", 10, "bold"),
            command=self._clear_history, corner_radius=13
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            title_row, text="✕", width=28, height=28,
            fg_color="transparent", hover_color=BORDER,
            text_color=TEXT_SM, font=("Segoe UI", 13),
            command=self._toggle_history_panel, corner_radius=14
        ).pack(side="right")

        search_row = ctk.CTkFrame(self.history_panel, fg_color="transparent")
        search_row.pack(fill="x", padx=16, pady=(0, 8))

        self.history_search_var = tk.StringVar()
        self.history_search_var.trace_add("write", lambda *_: self._refresh_history_list())

        self.history_search_entry = ctk.CTkEntry(
            search_row,
            textvariable=self.history_search_var,
            placeholder_text="🔍 ফিল্টার করুন...",
            width=340, height=32,
            font=("Segoe UI", 11),
            fg_color=BORDER, border_color=BLUE,
            text_color=WHITE
        )
        self.history_search_entry.pack(fill="x")

        self.history_scroll = ctk.CTkScrollableFrame(
            self.history_panel, fg_color="transparent",
            height=200, corner_radius=8
        )
        self.history_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._refresh_history_list()

    def _refresh_history_list(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        query = self.history_search_var.get().strip().lower() if hasattr(self, "history_search_var") else ""

        filtered = [
            e for e in reversed(self.search_history)
            if query in e.get("command", "").lower()
            or query in e.get("response", "").lower()
        ] if query else list(reversed(self.search_history))

        if not filtered:
            ctk.CTkLabel(
                self.history_scroll,
                text="কোনো ইতিহাস নেই।" if self.language == "bn" else "No history yet.",
                font=("Segoe UI", 11), text_color=TEXT_SM
            ).pack(pady=20)
            return

        for idx, entry in enumerate(filtered):
            self._build_history_row(entry, idx)

    def _build_history_row(self, entry, idx):
        row_bg = "navy" if idx % 2 == 0 else "darkslateblue"

        row = ctk.CTkFrame(self.history_scroll, fg_color=row_bg, corner_radius=8)
        row.pack(fill="x", pady=3, padx=2)

        ctk.CTkLabel(
            row, text=entry.get("time", ""),
            font=("Segoe UI", 9), text_color="lightgray", anchor="w"
        ).pack(anchor="w", padx=10, pady=(6, 0))

        cmd_text = entry.get("command", "")
        ctk.CTkLabel(
            row,
            text=f"🗣️  {cmd_text}",
            font=("Segoe UI", 11, "bold"), text_color="deepskyblue",
            anchor="w", wraplength=340, justify="left"
        ).pack(anchor="w", padx=10, pady=(2, 0))

        resp_text = entry.get("response", "")
        if resp_text:
            display = resp_text if len(resp_text) <= 80 else resp_text[:80] + "…"
            ctk.CTkLabel(
                row,
                text=f"🤖  {display}",
                font=("Segoe UI", 10), text_color="lightyellow",
                anchor="w", wraplength=340, justify="left"
            ).pack(anchor="w", padx=10, pady=(2, 8))

        row.bind("<Button-1>", lambda e, c=cmd_text: self._rerun_command(c))
        for child in row.winfo_children():
            child.bind("<Button-1>", lambda e, c=cmd_text: self._rerun_command(c))

    def _rerun_command(self, command):
        self._add_output(
            f"🔄 পুনরায় চালাচ্ছি: \"{command}\"" if self.language == "bn"
            else f"🔄 Re-running: \"{command}\"", color="goldenrod"
        )
        threading.Thread(target=lambda: self._process_command(command), daemon=True).start()

    def _clear_history(self):
        self.search_history = []
        self._save_history()
        self._refresh_history_list()
        self._add_output(
            "🗑️ ইতিহাস মুছে ফেলা হয়েছে।" if self.language == "bn"
            else "🗑️ History cleared.", color="darkorange"
        )

    def _toggle_history_panel(self):
        if self.history_panel_visible:
            self.history_panel.pack_forget()
            self.history_panel_visible = False
            self.history_btn.configure(text="🕐 ইতিহাস", fg_color="lightyellow", text_color="saddlebrown")
        else:
            if self.add_panel_visible:
                self.history_panel.pack(fill="x", after=self.add_panel)
            else:
                self.history_panel.pack(fill="x", after=self.top_bar)
            self.history_panel_visible = True
            self.history_btn.configure(text="✕ ইতিহাস বন্ধ", fg_color="mistyrose", text_color="crimson")
            self._refresh_history_list()

    def _toggle_add_panel(self):
        if self.add_panel_visible:
            self.add_panel.pack_forget()
            self.add_panel_visible = False
            self.add_btn.configure(text="➕ যোগ করুন", fg_color="honeydew", text_color="seagreen")
        else:
            self.add_panel.pack(fill="x", after=self.top_bar)
            self.add_panel_visible = True
            self.add_btn.configure(text="✕ বন্ধ করুন", fg_color="mistyrose", text_color="crimson")
            self._on_tab_change()

    def _animate(self):
        if not self.running:
            return

        self.canvas.delete("all")
        cx, cy, r = 60, 60, 28

        with self.state_lock:
            is_active    = self.is_active
            is_listening = self.is_listening

        if is_active:
            color = GREEN
        elif is_listening:
            color = BLUE
        else:
            color = "slategray"

        self.pulse_angle += 0.07
        pr = r + 8 + int(5 * math.sin(self.pulse_angle * 3))
        self.canvas.create_oval(cx-pr, cy-pr, cx+pr, cy+pr, outline=color, width=2)
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=WHITE, outline=color, width=3)

        icon = "✓" if is_active else ("👂" if is_listening else "🤖")
        self.canvas.create_text(cx, cy, text=icon, font=("Segoe UI Emoji", 18), fill=color)

        self.root.after(50, self._animate)

    def _start_wake_word_listener(self):
        threading.Thread(target=self._wake_word_loop, daemon=True).start()

    def _wake_word_loop(self):
        wake_words = [WAKE_WORD_EN, WAKE_WORD_BN]
        while self.running:
            with self.state_lock:
                skip = self.is_listening or self.is_active

            if skip:
                time.sleep(0.5)
                continue

            detected = self.speech_input.listen_for_wake_word(
                wake_words, timeout=2, phrase_time_limit=3,
                status_callback=self._update_status
            )
            if detected and self.running:
                self._on_wake_word_detected()

    def _on_wake_word_detected(self):
        with self.state_lock:
            self.is_active = True
            lang = self.language

        self.speech_output.speak("হ্যাঁ?" if lang == "bn" else "Yes?", blocking=False)
        self._update_status("🟢 সক্রিয় — কথা বলুন।" if lang == "bn" else "🟢 Active — speak now.")
        self._add_output(
            "--- জার্ভিস সক্রিয় ---" if lang == "bn" else "--- Jarvis Active ---",
            color="mediumseagreen"
        )
        time.sleep(0.8)
        self._listen_for_command()

    def _listen_for_command(self):
        with self.state_lock:
            self.is_listening = True
            lang = self.language

        self._update_status("👂 শুনছি..." if lang == "bn" else "👂 Listening...")

        text, success = self.speech_input.listen_once(
            timeout=8, phrase_time_limit=15,
            status_callback=self._update_status
        )

        with self.state_lock:
            self.is_listening = False
            self.is_active    = False
            lang = self.language

        if success:
            self._add_output(
                f"🗣️ আপনি বললেন: \"{text}\"" if lang == "bn"
                else f"🗣️ You said: \"{text}\"", color="deepskyblue"
            )
            self._process_command(text)
        else:
            self._add_output(f"⚠️ {text}", color="darkorange")
            self._update_status("অপেক্ষা করছি..." if lang == "bn" else "Waiting...")

    def _manual_listen(self):
        with self.state_lock:
            if self.is_listening:
                return
        threading.Thread(target=self._listen_for_command, daemon=True).start()

    def _process_command(self, command):
        with self.state_lock:
            lang = self.language

        self._update_status("🔄 চিন্তা করছি..." if lang == "bn" else "🔄 Processing...")
        response = self.command_proc.process(command)

        if response == "__QUIT__":
            self._shutdown()
            return

        if self.command_proc.language != lang:
            with self.state_lock:
                self.language = self.command_proc.language
                lang = self.language
            self.speech_input.set_language(lang)
            self.speech_output.set_language(lang)
            self._update_lang_button()

        self._add_output(
            f"🤖 জার্ভিস: {response}" if lang == "bn"
            else f"🤖 Jarvis: {response}", color="lightyellow"
        )
        self._add_to_history(command, response)
        self._update_status("বলছি..." if lang == "bn" else "Speaking...")
        threading.Thread(target=self._speak_and_finish, args=(response,), daemon=True).start()

    def _speak_and_finish(self, response):
        self.speech_output.speak(response, blocking=True)
        with self.state_lock:
            lang = self.language
        self._update_status(
            "অপেক্ষা করছি... \"জার্ভিস\" বলুন" if lang == "bn"
            else "Waiting... say \"Jarvis\""
        )

    def _update_status(self, text):
        self.root.after(0, lambda: self.status_label.configure(text=text))

    def _add_output(self, text, color=TEXT):
        def _do():
            self.output_text.configure(state="normal")
            self.output_text.insert("end", text + "\n\n")
            tag = f"tag_{self.output_text.index('end')}"
            self.output_text.tag_add(tag, f"end-{len(text)+2}c", "end-2c")
            self.output_text.tag_config(tag, foreground=color)
            self.output_text.see("end")
            self.output_text.configure(state="disabled")
        self.root.after(0, _do)

    def _toggle_language(self):
        with self.state_lock:
            self.language = "en" if self.language == "bn" else "bn"
            new_lang = self.language

        self.speech_input.set_language(new_lang)
        self.speech_output.set_language(new_lang)
        self.command_proc.set_language(new_lang)
        self.lang_btn.configure(text="🇬🇧 EN" if new_lang == "en" else "🇧🇩 BN")

        if new_lang == "en":
            self._add_output("Language changed to English.", color="mediumseagreen")
            self._update_status("Waiting... say \"Jarvis\"")
        else:
            self._add_output("ভাষা বাংলায় পরিবর্তিত।", color="mediumseagreen")
            self._update_status("অপেক্ষা করছি... \"জার্ভিস\" বলুন")

    def _update_lang_button(self):
        self.lang_btn.configure(text="🇧🇩 BN" if self.language == "bn" else "🇬🇧 EN")

    def _shutdown(self):
        self.running = False
        with self.state_lock:
            lang = self.language
        self.speech_output.speak(
            "বিদায়। আবার দেখা হবে।" if lang == "bn" else "Goodbye. See you later.",
            blocking=True
        )
        self._add_output("👋 বিদায়!" if lang == "bn" else "👋 Goodbye!", color="crimson")
        self.root.after(1500, self.root.destroy)

    def run(self):
        self.root.mainloop()
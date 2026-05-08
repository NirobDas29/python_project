import speech_recognition as sr


class SpeechInput:
    def __init__(self, language="bn"):
        self.set_language(language)
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = True

    def set_language(self, lang):
        if lang == "bn":
            self.lang_code = "bn-BD"
        else:
            self.lang_code = "en-US"
        self.language = lang

    def listen_once(self, timeout=5, phrase_time_limit=10, status_callback=None):
        r = sr.Recognizer()
        r.energy_threshold = self.recognizer.energy_threshold
        r.dynamic_energy_threshold = True

        try:
            with sr.Microphone() as source:
                if status_callback:
                    status_callback("🎙️ Adjusting for noise...")
                r.adjust_for_ambient_noise(source, duration=0.5)

                if status_callback:
                    status_callback("👂 শুনছি..." if self.language == "bn" else "👂 Listening...")

                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            if status_callback:
                status_callback("🔄 চিন্তা করছি..." if self.language == "bn" else "🔄 Processing...")

            text = r.recognize_google(audio, language=self.lang_code)
            return text, True

        except sr.WaitTimeoutError:
            msg = "কথা শুনতে পাইনি।" if self.language == "bn" else "No speech detected."
            return msg, False

        except sr.UnknownValueError:
            msg = "বুঝতে পারিনি। আবার বলুন।" if self.language == "bn" else "Could not understand. Say again."
            return msg, False

        except sr.RequestError as e:
            msg = f"Internet সংযোগ সমস্যা: {e}" if self.language == "bn" else f"Network error: {e}"
            return msg, False

        except Exception as e:
            msg = f"ত্রুটি: {e}" if self.language == "bn" else f"Error: {e}"
            return msg, False

    def listen_for_wake_word(self, wake_words, timeout=2, phrase_time_limit=3, status_callback=None):
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True

        try:
            with sr.Microphone() as source:
                if status_callback:
                    status_callback("⏳ অপেক্ষা করছি..." if self.language == "bn" else "⏳ Waiting...")
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            for lang_code in ["bn-BD", "en-US"]:
                try:
                    text = r.recognize_google(audio, language=lang_code)
                    for word in wake_words:
                        if word.lower() in text.lower():
                            return True
                except:
                    continue

            return False

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return False
        except Exception as e:
            print(f"Wake word error: {e}")
            return False
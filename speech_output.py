import os
import threading
import queue

try:
    from gtts import gTTS
    import pygame
    GTTS_AVAILABLE = True
    pygame_initialized = False
except ImportError:
    GTTS_AVAILABLE = False
    pygame_initialized = False
    print("gTTS or pygame not found. Run: pip install gtts pygame")

PYTTSX3_AVAILABLE = False
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    print("pyttsx3 not found. Run: pip install pyttsx3")


class SpeechOutput:
    def __init__(self, language="bn"):
        self.language = language
        self._is_speaking = False
        self._speak_lock = threading.Lock()
        self.pygame_initialized = False

        self._tts_queue = queue.Queue()
        self._worker_ready = threading.Event()
        self._worker_thread = threading.Thread(target=self._pyttsx3_worker, daemon=True)
        self._worker_thread.start()
        self._worker_ready.wait(timeout=5)

    def _pyttsx3_worker(self):
        """
        Dedicated thread that owns pyttsx3 for its entire lifetime.
        On Windows, SAPI5 is COM STA — the engine MUST be created and
        used in the same thread. CoInitialize is called here explicitly
        to guarantee a proper COM apartment for this thread.
        """
        engine = None

        if PYTTSX3_AVAILABLE:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                pass

            try:
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                if voices and len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 0.9)
            except Exception as e:
                print(f"pyttsx3 init failed: {e}")
                engine = None

        self._worker_ready.set()

        while True:
            item = self._tts_queue.get()
            if item is None:
                break

            text, done_event = item

            if engine:
                try:
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    print(f"pyttsx3 speak error: {e}")
                    self._gtts_fallback(text)
            else:
                self._gtts_fallback(text)

            done_event.set()
            self._tts_queue.task_done()

    def _gtts_fallback(self, text):
        if not GTTS_AVAILABLE:
            print(f"[SPEAK] {text}")
            return
        if not self.pygame_initialized:
            try:
                pygame.mixer.init()
                self.pygame_initialized = True
            except Exception as e:
                print(f"pygame init failed: {e}")
                print(f"[SPEAK] {text}")
                return
        temp_file = "jarvis_temp_en_fallback.mp3"
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file)
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"gTTS fallback error: {e}")
            print(f"[SPEAK] {text}")
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def set_language(self, lang):
        self.language = lang

    def speak(self, text, blocking=True):
        if not text:
            return
        if blocking:
            self._speak_internal(text)
        else:
            t = threading.Thread(target=self._speak_internal, args=(text,), daemon=True)
            t.start()

    def _speak_internal(self, text):
        with self._speak_lock:
            self._is_speaking = True
            try:
                if self.language == "bn":
                    self._speak_bangla(text)
                else:
                    self._speak_english(text)
            except Exception as e:
                print(f"Speech error: {e}")
            finally:
                self._is_speaking = False

    def _speak_bangla(self, text):
        if not GTTS_AVAILABLE:
            print(f"[SPEAK-BN] {text}")
            return
        if not self.pygame_initialized:
            try:
                pygame.mixer.init()
                self.pygame_initialized = True
            except Exception as e:
                print(f"pygame init failed: {e}")
                print(f"[SPEAK-BN] {text}")
                return
        temp_file = "jarvis_temp_bn.mp3"
        try:
            tts = gTTS(text=text, lang='bn', slow=False)
            tts.save(temp_file)
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"gTTS speak error: {e}")
            print(f"[SPEAK-BN] {text}")
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    def _speak_english(self, text):
        self._gtts_fallback(text)

    def stop(self):
        self._is_speaking = False
        try:
            if GTTS_AVAILABLE and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except:
            pass
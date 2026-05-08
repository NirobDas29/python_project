from gui import JarvisGUI
from speech_output import SpeechOutput
from config import DEFAULT_LANGUAGE


def main():
    tts = SpeechOutput(DEFAULT_LANGUAGE)

    if DEFAULT_LANGUAGE == "bn":
        intro = "আমি জার্ভিস। আপনার ভয়েস অ্যাসিস্ট্যান্ট। শুরু হচ্ছি।"
    else:
        intro = "I am Jarvis. Your voice assistant. Starting up."

    print("Jarvis Shobdo starting...")
    tts.speak(intro, blocking=True)

    app = JarvisGUI()
    app.run()


if __name__ == "__main__":
    main()
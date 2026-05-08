import pyttsx3

print("Hello, I am RoboSpeaker")

while True:
    x = input("What do you want to say? ")

    if x.lower() == "q":
        engine = pyttsx3.init()
        engine.say("Goodbye")
        engine.runAndWait()
        break

    engine = pyttsx3.init()   
    engine.say(x)
    engine.runAndWait()

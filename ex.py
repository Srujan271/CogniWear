from gtts import gTTS
import os

def text_to_speech(text, filename='output.mp3'):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    # Play the generated audio
    os.system("start " + filename)  # For Windows

if __name__ == "__main__":
    text = input("Enter the text to convert to speech: ")
    text_to_speech(text)
import os
import cv2
import google.generativeai as genai
from PIL import Image
import io
import pyttsx3
import speech_recognition as sr

os.environ['GOOGLE_API_KEY'] = "AIzaSyAipNFwJP5lAvmWjgy2QpaXCJPjX9BPOck"

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

def capture_image_from_camera():
    # Initialize the camera
    cap = cv2.VideoCapture(0)

    # Capture frame-by-frame
    ret, frame = cap.read()

    # Release the camera
    cap.release()

    # Convert the image to bytes
    ret, buffer = cv2.imencode('.jpg', frame)
    image_bytes = buffer.tobytes()

    return image_bytes  # Return the image bytes

def generate_image_description(image_bytes, question=None):
    # Convert bytes to PIL image
    image = Image.open(io.BytesIO(image_bytes))

    model = genai.GenerativeModel('gemini-pro-vision')
    if question:
        # Concatenate question with image
        input_data = [question, image]
    else:
        input_data = image

    # Generate content
    response = model.generate_content(input_data, stream=True)
    response.resolve()
    return response.text

def speak(text):
    """
    Helper function to convert text to speech and play it.
    
    Args:
        text: The text to be spoken.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    # Capture image from camera
    image = capture_image_from_camera()

    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Record audio from the microphone for asking the question
    with sr.Microphone() as source:
        speak("Ask a question about the image...")
        audio = recognizer.listen(source)

    # Use Google Web Speech API to convert speech to text
    try:
        speak("Recognizing question...")
        question = recognizer.recognize_google(audio)
        speak("Question: " + question)
    except sr.UnknownValueError:
        speak("Sorry, I could not understand what you said.")
        
    except sr.RequestError as e:
        speak("Error occurred; {0}".format(e))
        

    # Generate description
    description = generate_image_description(image, question)

    # Speak the description
    speak(description)

import os
import speech_recognition as sr
from threading import Thread
import cv2
from PIL import Image
import io
import pyttsx3
import time
import snowboydecoder

# Set up Snowboy models and sensitivity
snowboy_models = ["resources/run_cogniwear.pmdl", "resources/stop_cogniwear.pmdl"]
snowboy_sensitivity = [0.5, 0.5]

# Initialize Snowboy detector
detector = snowboydecoder.HotwordDetector(snowboy_models, sensitivity=snowboy_sensitivity)

# Set up Google API key
os.environ['GOOGLE_API_KEY'] = "YOUR_GOOGLE_API_KEY_HERE"

# Configure GenerativeAI
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to get user input from speech
def get_user_input_from_speech(prompt="Listening for command..."):
    text_to_speech(prompt)
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        text_to_speech(f"You said: {text}")
        return text.lower()  # Convert to lower case for easier comparison
    except sr.UnknownValueError:
        text_to_speech("Sorry, I could not understand what you said.")
        return ""
    except sr.RequestError as e:
        text_to_speech(f"Error occurred; {e}")
        return ""

# Function to convert text to speech
def text_to_speech(text):
    engine.say(text)
    engine.runAndWait()

# Function to capture image from camera
def capture_image_from_camera():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        text_to_speech("Failed to capture image.")
        return None
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes()

# Function to generate image description
def generate_image_description(image_bytes, question=None):
    image = Image.open(io.BytesIO(image_bytes))
    model = genai.GenerativeModel('gemini-pro-vision')
    input_data = [question, image] if question else [image]
    try:
        response = model.generate_content(input_data)
        return response.text
    except Exception as e:
        text_to_speech(f"Failed to generate image description: {e}")
        return "No description available."

# Function to capture and describe video
def capture_and_describe_video():
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    duration = 30  # seconds

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        ret, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()

        description = generate_image_description(image_bytes)
        text_to_speech(description)

        if time.time() - start_time > duration:
            break

        key = cv2.waitKey(1)
        if key == 13:  # Enter key code
            break

    cap.release()
    cv2.destroyAllWindows()

# Snowboy callback functions
def run_cogniwear_callback():
    global cogniwear_active
    cogniwear_active = True

def stop_cogniwear_callback():
    global cogniwear_active
    cogniwear_active = False

# Main loop control
if __name__ == "__main__":
    cogniwear_active = False
    while True:
        # Start Snowboy listener
        detector.start(detected_callback=[run_cogniwear_callback, stop_cogniwear_callback])

        # Loop until cogniwear is activated
        while not cogniwear_active:
            time.sleep(0.1)

        # Snowboy has detected "run cogniwear", now listen for commands
        while cogniwear_active:
            command = get_user_input_from_speech()

            if "activate microphone" in command:
                user_question = get_user_input_from_speech("What is your question?")
                if user_question:
                    model = genai.GenerativeModel('gemini-pro')
                    try:
                        response = model.generate_content([user_question])
                        # Truncate response to 50 words
                        response_text = ' '.join(response.text.split()[:50])
                        text_to_speech(response_text)
                    except Exception as e:
                        text_to_speech(f"Failed to generate response: {e}")

            elif "activate camera" in command:
                image = capture_image_from_camera()
                if image:
                    question = get_user_input_from_speech("Ask a question about the image...")
                    description = generate_image_description(image, question)
                    text_to_speech(description)

            elif "activate video" in command:
                capture_and_describe_video()

            elif "stop cogniwear" in command:
                cogniwear_active = False

            else:
                text_to_speech("No valid command detected. Please say 'activate microphone', 'activate camera', or 'activate video'.")

        # Stop Snowboy listener
        detector.terminate()

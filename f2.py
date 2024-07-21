import os
import cv2
import google.generativeai as genai
from PIL import Image
import io
import textwrap
from gtts import gTTS
import subprocess

os.environ['GOOGLE_API_KEY'] = "AIzaSyAipNFwJP5lAvmWjgy2QpaXCJPjX9BPOck"

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

def capture_and_describe_video():
    """
    Captures video from the camera, generates descriptions for each frame,
    and prints them.
    """
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        # Display the captured frame (optional)
        cv2.imshow('Video', frame)

        # Convert frame to bytes
        ret, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()

        # Generate description
        description = generate_image_description(image_bytes)

        # Speak the description
        speak(description)

        # Check for Enter key press
        key = cv2.waitKey(1)
        if key == 13:  # Enter key code
            break

    cap.release()
    cv2.destroyAllWindows()

def generate_image_description(image_bytes):
    """
    Generates a description for the given image bytes.

    Args:
        image_bytes: Bytes of the image.

    Returns:
        str: The generated description.
    """
    image = Image.open(io.BytesIO(image_bytes))
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(image)
    return response.text

def speak(text):
    """
    Converts text to speech and plays it.
    
    Args:
        text: The text to be spoken.
    """
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    # Play the generated audio
    if os.name == 'nt':  # For Windows
        subprocess.call(["start", "output.mp3"], shell=True)
    elif os.name == 'posix':  # For Linux
        subprocess.call(["xdg-open", "output.mp3"])

if __name__ == "__main__":
    capture_and_describe_video()

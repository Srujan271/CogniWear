import os
import cv2
import google.generativeai as genai
from PIL import Image
import io
import matplotlib.pyplot as plt
from gtts import gTTS

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

    return frame, image_bytes  # Return both the frame and image bytes


def generate_image_description(image_bytes):
    # Convert bytes to PIL image
    image = Image.open(io.BytesIO(image_bytes))

    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(image)
    
    # Convert the generated text to speech
    tts = gTTS(text=response.text, lang='en')
    tts.save('output.mp3')
    os.system("start output.mp3")  # For Windows

if __name__ == "__main__":
    # Capture image from camera
    frame, image = capture_image_from_camera()

    # Display the captured image
    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()

    # Generate audio description
    generate_image_description(image)

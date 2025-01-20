import json
import base64
import asyncio
import io
from channels.generic.websocket import AsyncWebsocketConsumer
from PIL import Image
import numpy as np
import pyttsx3
from .yolo import YOLO_Pred
import os
from pathlib import Path

# Get the base directory of the Django project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load YOLO model
MODEL_PATH = os.path.join(BASE_DIR, 'ml_models', 'best.onnx')
DATA_PATH = os.path.join(BASE_DIR, 'ml_models', 'data.yaml')

# Initialize YOLO model
yolo = YOLO_Pred(MODEL_PATH,DATA_PATH)

class DetectionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()  # Accept WebSocket connection

    async def disconnect(self, close_code):
        pass  # No special handling required on disconnect

    async def receive(self, bytes_data=None, text_data=None):
        if bytes_data:  
            # If client sends raw image (video frames)
            image = self.decode_binary_image(bytes_data)
        elif text_data:  
            # If client sends base64 image (for static images)
            text_data_json = json.loads(text_data)
            image_data = text_data_json.get('image')
            if not image_data:
                return
            image = self.decode_base64_image(image_data)
        else:
            return

        # Run YOLO Prediction
        _, detect_res = yolo.predictions(image)

        # Speak detected objects
        # for detection in detect_res:
        #     label = detection.get('label')
        #     if label:
        #         await self.speak_text(label)

        # Compute Manhattan distances
        distances = self.compute_manhattan_distance(detect_res)

        # Send back the response
        response_data = {
            'detections': detect_res,
            'distances': distances,
        }
        await self.send(text_data=json.dumps(response_data))

        # Small delay for handling real-time frames (preventing overload)
        await asyncio.sleep(0.02)  # Adjust frame rate based on performance

    def decode_binary_image(self, bytes_data):
        image = Image.open(io.BytesIO(bytes_data))
        return np.array(image)

    def decode_base64_image(self, img_str):
        img_data = base64.b64decode(img_str)
        image = Image.open(io.BytesIO(img_data))
        return np.array(image)

    def compute_manhattan_distance(self, detections):
        distances = []
        num_objects = len(detections)

        for i in range(num_objects):
            for j in range(i + 1, num_objects):
                obj1, obj2 = detections[i], detections[j]
                x1_center = (obj1['x1'] + obj1['x2']) // 2
                y1_center = (obj1['y1'] + obj1['y2']) // 2
                x2_center = (obj2['x1'] + obj2['x2']) // 2
                y2_center = (obj2['y1'] + obj2['y2']) // 2

                distance = abs(x1_center - x2_center) + abs(y1_center - y2_center)
                distances.append({
                    "object1": obj1['label'],
                    "object2": obj2['label'],
                    "distance": distance,
                })

        return distances

    # async def speak_text(self, text):
    #     def speak():
    #         engine = pyttsx3.init()
    #         engine.say(text)
    #         engine.runAndWait()
        
    #     await asyncio.to_thread(speak)

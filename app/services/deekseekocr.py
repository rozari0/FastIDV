import base64
import httpx
from app.core.config import settings


def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


class DeekSeekOCR:
    def __init__(self, image_path):
        self.image_path = image_path
        self.url = settings.OLLAMA_API_URL + "/api/generate"

    def process_image(self):
        image_base64 = encode_image(self.image_path)
        payload = {
            "model": "deepseek-ocr:latest",
            "prompt": "Extract all bengali & english text from this image.",
            "images": [image_base64],
            "stream": False,
        }

        response = httpx.post(self.url, json=payload)

        return response.json()["response"]

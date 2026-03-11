import base64
from json import loads

import aiofiles
import httpx

from app.core.config import settings
from app.schemas.user import NidData


class LLMService:
    def __init__(self):
        self.url = settings.OLLAMA_API_URL + "/api/generate"

    async def encode_image(self, path):
        async with aiofiles.open(path, "rb") as f:
            return base64.b64encode(await f.read()).decode("utf-8")

    async def process_image(self, image_path):
        image_base64 = await self.encode_image(image_path)
        payload = {
            "model": "deepseek-ocr:latest",
            "prompt": "Extract all text from this image.",
            "images": [image_base64],
            "stream": False,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=payload)
        response.raise_for_status()

        return response.json()["response"]

    async def process_data(self, prompt: str):
        payload = {
            "model": "qwen2.5:latest",
            "prompt": prompt,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self.url, json=payload)

        return loads(response.json()["response"])

    async def process_nid(self, text: str, schema: str) -> NidData:
        prompt = f"""
You are an information extraction system.

Extract data from OCR text and return ONLY valid JSON that follows this schema.
JSON Schema:
{schema}
Rules:
- Return JSON only
- Do not include explanations
- If a value is missing, return null
- Do not invent values
- Date should be in "%Y-%m-%d" format

OCR TEXT:
{text}
"""
        return await self.process_data(prompt)

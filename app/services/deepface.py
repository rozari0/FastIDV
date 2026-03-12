import base64

import aiofiles
import httpx


class DeepfaceService:
    def __init__(self):
        self.url = "http://localhost:5005"

    async def verify_face(self, image1_path, image2_path):
        async with httpx.AsyncClient(timeout=30) as client:
            async with (
                aiofiles.open(image1_path, "rb") as f1,
                aiofiles.open(image2_path, "rb") as f2,
            ):
                img1_bytes = await f1.read()
                img2_bytes = await f2.read()
                files = {
                    "img1": ("image1.png", img1_bytes, "image/png"),
                    "img2": ("image2.jpg", img2_bytes, "image/jpeg"),
                }
                response = await client.post(self.url + "/verify", files=files)
        print(response.text)
        response.raise_for_status()
        return response.json()

    async def check_spoof(self, img_path):
        return
        img_base64 = await self.encode_image(img_path)
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                self.url + "/analyze",
                json={"img": img_base64, "anti_spoofing": True},
            )

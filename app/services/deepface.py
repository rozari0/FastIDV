import aiofiles
import httpx


class DeepfaceService:
    def __init__(self):
        self.url = "http://localhost:8008"

    async def verify_face(self, image1_path, image2_path):
        async with httpx.AsyncClient(timeout=30) as client:
            async with (
                aiofiles.open(image1_path, "rb") as f1,
                aiofiles.open(image2_path, "rb") as f2,
            ):
                img1_bytes = await f1.read()
                img2_bytes = await f2.read()
                files = {
                    "img_1": ("image1.png", img1_bytes, "image/png"),
                    "img_2": ("image2.jpg", img2_bytes, "image/jpeg"),
                }
                response = await client.post(self.url + "/verify/", files=files)
        print(response.text)
        response.raise_for_status()
        return response.json()

    async def check_spoof(self, img_path) -> bool:
        async with httpx.AsyncClient(timeout=20) as client:
            async with aiofiles.open(img_path, "rb") as f:
                img_bytes = await f.read()
                files = {"img": ("image.png", img_bytes, "image/png")}
                response = await client.post(
                    self.url + "/analyze/", data={"anti_spoofing": True}, files=files
                )
                return True if response.text == "true" else False

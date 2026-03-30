import os
import uuid
import httpx
from io import BytesIO
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from twilio.rest import Client
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

app = FastAPI()

twilio_client = Client(os.environ["TWILIO_SID"], os.environ["TWILIO_AUTH"])

TWILIO_FROM = "whatsapp:+14155238886"
TWILIO_TO = "whatsapp:+447300130606"
APP_URL = os.environ.get("APP_URL", "https://tattlableads.onrender.com")

image_store = {}


@app.get("/")
def health():
    return {"status": "live"}


@app.get("/media/{image_id}")
def serve_image(image_id: str):
    data = image_store.get(image_id)
    if not data:
        return Response(status_code=404)
    return Response(content=data, media_type="image/jpeg")


class Lead(BaseModel):
    name: str
    phone: str
    message: str
    image_urls: list[str] = []


def convert_to_jpeg(url: str) -> str | None:
    try:
        r = httpx.get(url, timeout=15, follow_redirects=True)
        image = Image.open(BytesIO(r.content)).convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        image_id = str(uuid.uuid4())
        image_store[image_id] = buffer.getvalue()
        return f"{APP_URL}/media/{image_id}"
    except Exception:
        return None


@app.post("/lead")
def receive_lead(lead: Lead):
    print(f"image_urls received: {lead.image_urls}", flush=True)
    body = f"🔥 NEW WEBSITE LEAD\n\nName: {lead.name}\nPhone: {lead.phone}\nMessage: {lead.message}"

    converted = [u for u in (convert_to_jpeg(url) for url in lead.image_urls) if u]

    # First message: text + first image (if any)
    twilio_client.messages.create(
        from_=TWILIO_FROM,
        to=TWILIO_TO,
        body=body,
        **({"media_url": [converted[0]]} if converted else {}),
    )

    # Remaining images: one message each
    for image_url in converted[1:]:
        twilio_client.messages.create(
            from_=TWILIO_FROM,
            to=TWILIO_TO,
            body="",
            media_url=[image_url],
        )

    return {"status": "sent"}

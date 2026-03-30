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
    except Exception as e:
        print(f"Image conversion failed: {e}", flush=True)
        return None


def send_whatsapp(body: str, image_url: str | None):
    converted = convert_to_jpeg(image_url) if image_url else None
    kwargs = {"from_": TWILIO_FROM, "to": TWILIO_TO, "body": body}
    if converted:
        kwargs["media_url"] = [converted]
    twilio_client.messages.create(**kwargs)


@app.post("/lead")
def receive_lead(lead: Lead):
    print(f"Lead received. image_urls: {lead.image_urls}", flush=True)
    body = f"🔥 NEW WEBSITE LEAD\n\nName: {lead.name}\nPhone: {lead.phone}\nMessage: {lead.message}"
    image_url = lead.image_urls[0] if lead.image_urls else None
    send_whatsapp(body, image_url)
    return {"status": "sent"}

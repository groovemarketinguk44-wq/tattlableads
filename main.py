import os
from fastapi import FastAPI
from pydantic import BaseModel
from twilio.rest import Client

app = FastAPI()

twilio_client = Client(os.environ["TWILIO_SID"], os.environ["TWILIO_AUTH"])

TWILIO_FROM = "whatsapp:+14155238886"
TWILIO_TO = "whatsapp:+447300130606"

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".mp4", ".pdf")


def is_supported(url: str) -> bool:
    path = url.split("?")[0].lower()
    return any(path.endswith(ext) for ext in SUPPORTED_FORMATS)


@app.get("/")
def health():
    return {"status": "live"}


class Lead(BaseModel):
    name: str
    phone: str
    message: str
    image_urls: list[str] = []


@app.post("/lead")
def receive_lead(lead: Lead):
    print(f"Lead received. image_urls: {lead.image_urls}", flush=True)

    supported = [u for u in lead.image_urls if is_supported(u)]
    unsupported = [u for u in lead.image_urls if not is_supported(u)]

    body = f"🔥 NEW WEBSITE LEAD\n\nName: {lead.name}\nPhone: {lead.phone}\nMessage: {lead.message}"

    if unsupported:
        body += "\n\n📎 Design files:\n" + "\n".join(unsupported)

    # First message: text + first supported image
    twilio_client.messages.create(
        from_=TWILIO_FROM,
        to=TWILIO_TO,
        body=body,
        **({"media_url": [supported[0]]} if supported else {}),
    )

    # Remaining images: one message each
    for url in supported[1:]:
        twilio_client.messages.create(
            from_=TWILIO_FROM,
            to=TWILIO_TO,
            body="📎",
            media_url=[url],
        )

    return {"status": "sent"}

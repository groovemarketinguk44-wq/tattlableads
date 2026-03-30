import os
from fastapi import FastAPI
from pydantic import BaseModel
from twilio.rest import Client

app = FastAPI()

twilio_client = Client(os.environ["TWILIO_SID"], os.environ["TWILIO_AUTH"])

TWILIO_FROM = "whatsapp:+14155238886"
TWILIO_TO = "whatsapp:+447300130606"


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
    body = f"🔥 NEW WEBSITE LEAD\n\nName: {lead.name}\nPhone: {lead.phone}\nMessage: {lead.message}"
    kwargs = {"from_": TWILIO_FROM, "to": TWILIO_TO, "body": body}
    if lead.image_urls:
        kwargs["media_url"] = lead.image_urls
    twilio_client.messages.create(**kwargs)
    return {"status": "sent"}

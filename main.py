import os
from fastapi import FastAPI, Form
from twilio.rest import Client

app = FastAPI()

twilio_client = Client(os.environ["TWILIO_SID"], os.environ["TWILIO_AUTH"])

TWILIO_FROM = "whatsapp:+14155238886"
TWILIO_TO = "whatsapp:+447300130606"


@app.get("/")
def health():
    return {"status": "live"}


@app.post("/lead")
def receive_lead(
    name: str = Form(...),
    phone: str = Form(...),
    message: str = Form(...),
):
    body = f"🔥 NEW WEBSITE LEAD\n\nName: {name}\nPhone: {phone}\nMessage: {message}"
    twilio_client.messages.create(from_=TWILIO_FROM, to=TWILIO_TO, body=body)
    return {"status": "sent"}

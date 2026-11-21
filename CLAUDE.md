# TattLabLeads

TattLab lead capture helper (Twilio SMS + image upload).

## Stack

Single-file FastAPI (main.py)

## Commands

```bash
# install
pip install -r requirements.txt
# run
uvicorn main:app --reload
# test
(no automated tests yet: run it and check the changed pages by hand)
```

## Deploy

No deploy config in repo.

## Environment variables (names only; values live in Fly secrets / local .env, never in git)

APP_URL TWILIO_SID TWILIO_AUTH

Needed in a cloud session: none

## Conventions

- Work on a branch and open a PR; Ben merges. Never commit secrets or .env files.
- Keep changes small and explain them in plain words.
- Ben's defaults for his apps: OneSignal push alerts, an admin Visitors tab, full SEO (landing pages, sitemap) where it fits.

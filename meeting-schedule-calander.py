from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import json

app = FastAPI()

SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = "http://localhost:8000/oauth2callback"   # change later on VM

# ----------- INPUT MODEL ----------
class Meeting(BaseModel):
    topic: str
    date: str          # YYYY-MM-DD
    start_time: str    # HH:MM 24hr
    end_time: str      # HH:MM 24hr
    timezone: str = "Asia/Kolkata"


# ----------- STEP 1: START AUTH ----------
@app.get("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(auth_url)


# ----------- STEP 2: HANDLE CALLBACK ----------
@app.get("/oauth2callback")
def oauth2callback(code: str):

    flow = Flow.from_client_secrets_file(
        "credentials.json",
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    flow.fetch_token(code=code)

    creds = flow.credentials

    # save token
    with open("token.json", "w") as f:
        f.write(creds.to_json())

    return "Google Calendar authorization successful! You can now call /schedule"


# ----------- UTILITY ----------
def get_calendar_service():
    if not os.path.exists("token.json"):
        raise HTTPException(401, "Not authorized. Visit /authorize first.")

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("calendar", "v3", credentials=creds)
    return service


# ----------- STEP 3: CREATE EVENT ----------
@app.post("/schedule")
def schedule(meeting: Meeting):

    service = get_calendar_service()

    start = f"{meeting.date}T{meeting.start_time}:00"
    end = f"{meeting.date}T{meeting.end_time}:00"

    event = {
        "summary": meeting.topic,
        "start": {
            "dateTime": start,
            "timeZone": meeting.timezone,
        },
        "end": {
            "dateTime": end,
            "timeZone": meeting.timezone,
        }
    }

    created = service.events().insert(calendarId="primary", body=event).execute()

    return {
        "status": "success",
        "eventLink": created.get("htmlLink"),
        "eventId": created.get("id")
    }

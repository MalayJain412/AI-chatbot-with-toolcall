from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
import json
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

app = FastAPI()

GOOGLE_CLIENT_CONFIG = json.load(open("client_secret_sheets.json"))

REDIRECT_URI = "http://localhost:8000/oauth/callback"

SCOPES =[
    "https://www.googleapis.com/auth/speadsheets"
]

@app.get("/")
def home():
    return {"message": "Welcome to the Google Sheets OAuth2 Demo!"}

@app.get("/login")
def login():
    """
    Step 1: Redirect the user to Google for login & cosent.
    """

    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=SCOPES,
    )

    flow.redirect_uri = REDIRECT_URI
    
    authorization_url, state = flow.authorization_url(
        access_type = "offline", # ensures refresh token is returned
        include_granted_scopes = "true"
    )

    # store state securely later - here just return redirect
    return RedirectResponse(url=authorization_url)

@app.get("/oauth/callback")
def oauth_callback(request: Request):
    """
    Step 2: Google redirects here with ?code=...
    We exchange code -> access-token + refresh_token
    """

    flow = Flow.from_client_config(
        GOOGLE_CLIENT_CONFIG,
        scopes=SCOPES
    )

    flow.redirect_uri = REDIRECT_URI

    authorization_response = str(request.url)

    flow.fetch_token(authorization_response=authorization_response)

    credentials: Credentials = flow.credentials

    # Token received
    token_data = {
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_expiry": str(credentials.expiry),
        "scope":credentials.scopes
    }

    # TODO : Save refresh_token securely in DB

    return JSONResponse(
        {
            "message":"Google OAuth login successful!",
            "token_details": token_data
        }
    )
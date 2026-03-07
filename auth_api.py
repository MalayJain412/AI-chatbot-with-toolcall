from google_auth_oauthlib.flow import InstalledAppFlow

# add the SCOPES you need for your application (usually the apis you have activated in your Google Cloud Console)

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials.json", # or the file you have saved your credentials in
    SCOPES
)

# creds = flow.run_local_server(port=8080)
# on vm
creds = flow.run_local_server(
    port=8080,
    open_browser=False
)

with open("token.json", "w") as token:
    token.write(creds.to_json())
# Google Sheets API Authentication Guide (Python + LangChain)

This document explains how to authorize a Python application to access Google Sheets using OAuth2. These steps also work if you are already using Google Calendar API.

---

## 1. Enable Google Sheets API

1. Go to **Google Cloud Console**
2. Navigate to:

```
APIs & Services → Library
```

3. Search for:

```
Google Sheets API
```

4. Click **Enable**

---

## 2. Create OAuth Credentials

Navigate to:

```
APIs & Services → Credentials
```

Click:

```
Create Credentials → OAuth Client ID
```

Choose:

```
Application Type: Desktop App
```

Download the JSON file.

Rename it to:

```
credentials.json
```

Place it in your project root:

```
project/
 ├── main.py
 ├── tools.py
 ├── credentials.json
```

---

## 3. Install Required Libraries

```
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## 4. Create Authorization Script

Create a file:

```
auth_sheets.py
```

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

flow = InstalledAppFlow.from_client_secrets_file(
    "credentials.json",
    SCOPES
)

creds = flow.run_local_server(port=8080)

with open("token.json", "w") as token:
    token.write(creds.to_json())

print("Authorization successful. token.json created.")
```

---

## 5. Run Authorization

```
python auth_sheets.py
```

A browser window will open.

Login with your Google account and allow access.

After success you will get:

```
token.json
```

Project structure:

```
project/
 ├── main.py
 ├── tools.py
 ├── credentials.json
 ├── token.json
```

---

## 6. Access Google Sheets from Python

Example code:

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(
    "token.json",
    ["https://www.googleapis.com/auth/spreadsheets.readonly"]
)

service = build("sheets", "v4", credentials=creds)

SPREADSHEET_ID = "YOUR_SHEET_ID"

result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range="Sheet1!A1:C20"
).execute()

print(result.get("values", []))
```

---

## 7. Find Spreadsheet ID

Example sheet URL:

```
https://docs.google.com/spreadsheets/d/1ABCxyz123456/edit#gid=0
```

Spreadsheet ID is:

```
1ABCxyz123456
```

---

## 8. Notes

• The same OAuth credential can access multiple Google APIs.

• Calendar and Sheets can share the same `token.json`.

• If scopes change, delete `token.json` and run authorization again.

---

End of guide.


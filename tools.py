from langchain.tools import tool
import requests
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import sender_email, sender_password, admin_email
from templates import USER_EMAIL_TEMPLATE, ADMIN_EMAIL_TEMPLATE
import re
import dateparser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)

@tool
def web_search(query: str) -> str:
    """General web search. 
    DO NOT use this tool for Malay or Malay Jain related questions 
    unless get_malay_info fails.
    """
    logger.info(f"Performing web search for query: {query}")
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        logger.info(f"Making request to URL: {url}")
        res = requests.get(url, timeout=10)
        logger.info(f"Received response with status code: {res.status_code}")
        result = res.text
        logger.info(f"Search completed successfully, result length: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Web search failed: {str(e)}")
        return f"Search failed: {str(e)}"

@tool
def get_malay_info(dummy: str) ->str:
    """USE THIS TOOL FIRST when the user asks about Malay or Malay Jain.
    This tool returns the official verified profile.
    Do NOT use web_search for Malay Jain unless this tool returns nothing.
    The input is ignored.
    """
    logger.info("Retrieving Malay information from malay.txt")
    try:
        with open("malay.txt", "r", encoding = "utf-8") as file:
            content = file.read()
            logger.info(f"Successfully read malay.txt, content length: {len(content)}")
            return content
    except Exception as e:
        logger.error(f"Failed to read malay.txt: {str(e)}")
        return f"Malay info not available: {str(e)}"

@tool
def get_user_email_id(query: str) -> str:
    """Use this tool when the user asks for the email / mail id of a user.
    Supported users:
    - Malay Jain / Malay
    - Aniket / Aniket Kumar / Aniket Mishra / Aniket Kumar Mishra

    Return ONLY the email address string, nothing else.
    """

    logger.info(f"Resolving email from query: {query}")

    q = query.lower()

    if "malay" in q:
        return "malayjain1234@gmail.com"

    if "aniket" in q:
        return "anni990@gmail.com"

    return "Email not found"


# --------------------------------------
# Email Tools
# --------------------------------------

email_store = {}

@tool
def save_email_details(text: str) -> str:
    """
    Extract and save email details from user request.

    Use this tool FIRST when the user asks to send an email.

    Input example:
    "send an email to anni990@gmail.com saying 'Hello from Malay'"

    This tool will:
    - extract the recipient email
    - extract the message content (inside quotes OR after 'saying')
    - store details in memory
    - always send a complete message
    """
    
    logger.info(f"Saving email details from: {text}")

    # --- Extract ALL emails ---
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)

    if not emails:
        return "No valid email found in message."

    # --- Extract message content ---
    msg_match = re.search(
        r"'(.*?)'|\"(.*?)\"|saying\s(.+)|message\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )

    if msg_match:
        body = next(g for g in msg_match.groups() if g).strip()
    else:
        body = "Hello!"

    subject = "New Message"

    email_store["to_emails"] = emails
    email_store["subject"] = subject
    email_store["body_html"] = body

    return f"Emails saved for: {', '.join(emails)}"

@tool
def send_email(trigger: str) -> str:
    """
    Send the MOST RECENT saved email to the intended recipient.
    ALSO send a notification email to the admin.

    Use this tool ONLY AFTER save_email_details has run.
    
    - always send a complete message

    Input is ignored (pass any string).
    """

    try:
        to_emails = email_store.get("to_emails")
        subject = email_store.get("subject")
        body_html = email_store.get("body_html")

        if not to_emails:
            return "No emails saved. Run save_email_details first."

        user_html = USER_EMAIL_TEMPLATE.replace("{message}", body_html)

        admin_html = (
            ADMIN_EMAIL_TEMPLATE
                .replace("{to_email}", ", ".join(to_emails))
                .replace("{subject}", subject)
                .replace("{message}", body_html)
        )

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # send to each user
        for email in to_emails:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = email
            msg["Subject"] = subject
            msg.attach(MIMEText(user_html, "html"))

            server.sendmail(sender_email, email, msg.as_string())

        # send admin
        admin_msg = MIMEMultipart()
        admin_msg["From"] = sender_email
        admin_msg["To"] = admin_email
        admin_msg["Subject"] = f"Email Sent To {', '.join(to_emails)}"
        admin_msg.attach(MIMEText(admin_html, "html"))

        server.sendmail(sender_email, admin_email, admin_msg.as_string())

        server.quit()

        return f"Email sent to {', '.join(to_emails)} and admin notified."

    except Exception as e:
        logger.error(e)
        return f"Failed to send email: {str(e)}"
    
''' Old send_email implementation with only sending email to receiver

# @tool
# def send_email(trigger: str) -> str:
#     """
#     Send the MOST RECENTLY saved email.

#     Use this tool ONLY AFTER save_email_details has run.

#     Input is ignored. Pass any string.
#     """

#     try:
#         to_email = email_store.get("to_email")
#         subject = email_store.get("subject")
#         body_html = email_store.get("body_html")

#         if not to_email:
#             return "No email saved. Run save_email_details first."

#         message = MIMEMultipart()
#         message["From"] = sender_email
#         message["To"] = to_email
#         message["Subject"] = subject
#         message.attach(MIMEText(body_html, "html"))

#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()
#         server.login(sender_email, sender_password)
#         server.sendmail(sender_email, to_email, message.as_string())
#         server.quit()

#         return f"Email sent successfully to {to_email}"

#     except Exception as e:
#         logger.error(e)
#         return f"Failed to send email: {str(e)}"
'''

# # --------------------------------------
# # Google Calander Tools
# # --------------------------------------

# meeting_store = {}


# # ---------- VALIDATORS ----------
# def validate_date(date_str):
#     try:
#         datetime.strptime(date_str, "%Y-%m-%d")
#         return True
#     except:
#         return False


# def validate_time(t):
#     return bool(re.fullmatch(r"\d{2}:\d{2}", t))


# # ---------- TOOL #1 ----------
# @tool
# def save_meeting_details(meeting_json: str) -> str:
#     """
#     Save a meeting draft from structured JSON.

#     The LLM MUST pass JSON string with this structure:

#     {
#       "topic": "Friday AI architecture",
#       "date": "2025-12-28",
#       "start_time": "16:00",
#       "end_time": "17:00",
#       "timezone": "Asia/Kolkata",
#       "attendees": ["email1@example.com"]
#     }

#     Rules:
#     - date MUST be YYYY-MM-DD
#     - start_time / end_time MUST be HH:MM 24-hour
#     - timezone default = Asia/Kolkata
#     - attendees is optional
#     """

#     try:
#         data = json.loads(meeting_json)
#     except:
#         return "❌ Invalid JSON. Please resend."

#     topic = data.get("topic", "Meeting")
#     date = data.get("date")
#     start = data.get("start_time")
#     end = data.get("end_time")
#     tz = data.get("timezone", "Asia/Kolkata")
#     attendees = data.get("attendees", [])

#     # -------- VALIDATION --------
#     if not date or not validate_date(date):
#         return "❌ Invalid date. Must be YYYY-MM-DD."

#     if not start or not validate_time(start):
#         return "❌ Invalid start_time. Must be HH:MM (24hr)."

#     if not end or not validate_time(end):
#         return "❌ Invalid end_time. Must be HH:MM (24hr)."

#     # save draft
#     meeting_store.update({
#         "topic": topic,
#         "date": date,
#         "start_time": start,
#         "end_time": end,
#         "timezone": tz,
#         "attendees": attendees
#     })

#     return f"""
# 📝 Meeting Draft Created

# Title: {topic}
# Date: {date}
# Time: {start} → {end} ({tz})

# Say **"confirm meeting"** to schedule.
# """


# # ---------- TOOL #2 ----------
# @tool
# def schedule_meeting(trigger: str) -> str:
#     """
#     Schedule the MOST RECENT draft meeting to Google Calendar.

#     Only run AFTER save_meeting_details.
#     """

#     if not meeting_store:
#         return "❌ No meeting draft found."

#     if not os.path.exists("token.json"):
#         return "❌ Google Calendar not authorized."

#     creds = Credentials.from_authorized_user_file("token.json")
#     service = build("calendar", "v3", credentials=creds)

#     start = f"{meeting_store['date']}T{meeting_store['start_time']}:00"
#     end = f"{meeting_store['date']}T{meeting_store['end_time']}:00"

#     event = {
#         "summary": meeting_store["topic"],
#         "start": {"dateTime": start, "timeZone": meeting_store["timezone"]},
#         "end": {"dateTime": end, "timeZone": meeting_store["timezone"]},
#     }

#     # optionally add attendees
#     if meeting_store.get("attendees"):
#         event["attendees"] = [
#             {"email": e} for e in meeting_store["attendees"]
#         ]

#     created = service.events().insert(
#         calendarId="primary",
#         body=event
#     ).execute()

#     return f"""
# ✅ Meeting Scheduled!

# Topic: {meeting_store['topic']}
# Date: {meeting_store['date']}
# Time: {meeting_store['start_time']} → {meeting_store['end_time']}

# 📍 Timezone: {meeting_store['timezone']}

# 🔗 Event Link:
# {created.get("htmlLink")}
# """
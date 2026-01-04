from fastapi import FastAPI, HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SMTP_SERVER = "smtp.titan.email"
SMTP_PORT = 587

SENDER_EMAIL = os.getenv("TITAN_SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("TITAN_APP_PASSWORD")

print('Mail:',repr(SENDER_EMAIL))
print("PWD:", repr(SENDER_PASSWORD[:10]),".....")

class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str
    is_html: bool = True
    
    
@app.get("/")
def status():
    return {"status":"Application running successfully"}



@app.post("/send-email")
def send_email(email: EmailRequest):
    
    if not SENDER_PASSWORD or not SENDER_EMAIL:
        raise HTTPException(status_code=500, detail="Email credentials not configured")
    
    # Build message
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = email.to
    msg["Subject"] = email.subject
    
    if email.is_html:
        msg.attach(MIMEText(email.body, "html" ))
    else:
        msg.attach(MIMEText(email.body, "plain" ))
        
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL,email.to, msg.as_string())
        server.quit()
        
        return {"message":"Email sent successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))